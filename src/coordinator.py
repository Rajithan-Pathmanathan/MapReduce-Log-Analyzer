"""
src/coordinator.py
==================
MapReduce job execution coordinator and pipeline orchestrator.

Primary Ownership: Member 1 (Coordinator + Map Phase)
Integration Touchpoints: Integrates with Shuffle & Reducer (Member 2) and Output (Member 3)

Responsibilities:
- Coordinate the lifecycle of a complete MapReduce job.
- Validate inputs and initialize input file splits via InputManager.
- Spawn and manage parallel Map worker processes using multiprocessing.
- Collect intermediate key-value results from Map workers.
- Hand over intermediate results to ShuffleManager (Member 2) for grouping and partitioning.
- Spawn and manage parallel Reduce worker processes using multiprocessing.
- Collect and pass reduced partitions to OutputManager (Member 3).
- Measure wall-clock execution time for individual phases and total runtime.
"""

import multiprocessing
import time
from functools import partial
from typing import Any, Dict, List, Tuple
from src.config import Config
from src.input_manager import InputManager, InputSplit, create_byte_splits
from src.mapper import map_split_worker
from src.reducer import reduce_worker
from src.output_manager import OutputManager
from src.shuffle import ShuffleManager


class Coordinator:
    """Orchestrates parallel MapReduce execution across simulated worker processes."""

    def __init__(self, config: Config):
        """
        Initialize the Coordinator with system configuration.

        :param config: Config instance containing paths, worker counts, and settings.
        """
        self.config = config
        self.input_manager = InputManager(config.input_dir)
        self.shuffle_manager = ShuffleManager(config.reduce_workers)
        self.output_manager = OutputManager(config.output_dir, config.output_file_name)

        # Performance and execution metrics
        self.metrics: Dict[str, Any] = {
            "input_files_count": 0,
            "total_input_bytes": 0,
            "total_input_lines": 0,
            "input_splits": 0,
            "intermediate_pairs": 0,
            "map_workers": config.map_workers,
            "reduce_workers": config.reduce_workers,
            "unique_keys": 0,
            "map_time_seconds": 0.0,
            "shuffle_time_seconds": 0.0,
            "reduce_time_seconds": 0.0,
            "total_execution_time_seconds": 0.0,
            "top_n": config.top_n_results,
        }

    def _log(self, message: str) -> None:
        if self.config.verbose:
            print(f"[Coordinator] {message}")

    def run_map_phase(self, splits: List[InputSplit]) -> List[Tuple[str, int]]:
        """
        Launch parallel Map worker processes to process input splits.

        Splits are handed to a process pool; each worker reads only its own
        byte range. Results are re-ordered by split_id so output is
        deterministic regardless of which worker finished first.

        :param splits: Byte-range InputSplits from create_byte_splits().
        :return: Flattened list of all emitted (key, value) pairs.
        """
        if not splits:
            return []
        worker = partial(
            map_split_worker,
            case_sensitive=self.config.case_sensitive,
            min_word_length=self.config.min_word_length,
        )
        num_workers = min(self.config.map_workers, len(splits))
        with multiprocessing.Pool(processes=num_workers) as pool:
            outputs = pool.map(worker, splits)

        pairs: List[Tuple[str, int]] = []
        for out in sorted(outputs, key=lambda o: o["split_id"]):
            self._log(
                f"split {out['split_id']} done by pid {out['worker_pid']}: "
                f"{out['lines']} lines, {len(out['pairs'])} pairs, {out['elapsed']:.3f}s"
            )
            pairs.extend(out["pairs"])
        self.metrics["map_worker_pids"] = sorted({o["worker_pid"] for o in outputs})
        return pairs

    def run_map_stage(self) -> List[Tuple[str, int]]:
        """
        Member 1 stage: discover + measure input, split it, run parallel Map.

        This is the interface handed to Member 2: a flat list of
        (term, 1) tuples ready for ShuffleManager.shuffle_and_partition().
        All numbers written to self.metrics are measured, never estimated.

        :return: Intermediate (key, value) pairs from every Map worker.
        :raises FileNotFoundError / ValueError: from InputManager.validate_directory().
        """
        self.input_manager.validate_directory()
        files = self.input_manager.discover_files()
        measured = self.input_manager.measure_input(files)
        splits = create_byte_splits(files, self.config.split_size_bytes)

        self.metrics["input_files_count"] = measured["file_count"]
        self.metrics["total_input_bytes"] = measured["total_bytes"]
        self.metrics["total_input_lines"] = measured["total_lines"]
        self.metrics["input_splits"] = len(splits)
        self._log(
            f"{measured['file_count']} input files, {measured['total_bytes']} bytes, "
            f"{measured['total_lines']} lines -> {len(splits)} splits, "
            f"{self.config.map_workers} Map workers"
        )

        map_start = time.perf_counter()
        pairs = self.run_map_phase(splits)
        self.metrics["map_time_seconds"] = time.perf_counter() - map_start
        self.metrics["intermediate_pairs"] = len(pairs)
        self._log(
            f"Map phase finished: {len(pairs)} intermediate pairs in "
            f"{self.metrics['map_time_seconds']:.3f}s"
        )
        return pairs

    def run_reduce_phase(
        self, partitions: Dict[int, Dict[str, List[int]]]
    ) -> List[List[Tuple[str, int]]]:
        """
        Launch parallel Reduce worker processes to aggregate partitioned data.

        :param partitions: Mapping from reducer ID to partition payload.
        :return: List of results collected from each reduce worker.
        """
        tasks = [
            (partitions.get(r_id, {}), r_id)
            for r_id in range(self.config.reduce_workers)
        ]
        with multiprocessing.Pool(processes=self.config.reduce_workers) as pool:
            outputs = pool.starmap(reduce_worker, tasks)
        for r_id, out in enumerate(outputs):
            self._log(f"reducer {r_id} done: {len(out)} keys")
        return outputs

    def execute_job(self) -> Dict[str, Any]:
        """
        Execute the end-to-end MapReduce job pipeline:
        1. Discover & validate input files
        2. Create input splits
        3. Parallel Map phase
        4. Shuffle & Partition phase
        5. Parallel Reduce phase
        6. Consolidate results & output summary

        :return: Execution summary dictionary including metrics and top results.
        """
        job_start = time.perf_counter()

        # Steps 1-3: Member 1 (input, splits, parallel Map)
        intermediate_pairs = self.run_map_stage()

        # Step 4: Shuffle & Partition (Member 2)
        shuffle_start = time.perf_counter()
        partitions = self.shuffle_manager.shuffle_and_partition(intermediate_pairs)
        self.metrics["shuffle_time_seconds"] = time.perf_counter() - shuffle_start
        self.metrics["keys_per_reducer"] = [len(partitions[r]) for r in sorted(partitions)]
        self._log(
            f"Shuffle finished: {sum(self.metrics['keys_per_reducer'])} unique keys -> "
            f"{self.config.reduce_workers} partitions {self.metrics['keys_per_reducer']} "
            f"in {self.metrics['shuffle_time_seconds']:.3f}s"
        )

        # Step 5: Reduce (Member 2)
        reduce_start = time.perf_counter()
        reducer_results = self.run_reduce_phase(partitions)
        self.metrics["reduce_time_seconds"] = time.perf_counter() - reduce_start

        # Step 6: Output (Member 3)
        sorted_results = self.output_manager.consolidate_and_sort(reducer_results)
        self.metrics["unique_keys"] = len(sorted_results)
        self.metrics["total_execution_time_seconds"] = time.perf_counter() - job_start
        self.output_manager.write_output_file(sorted_results, self.metrics)
        self.output_manager.display_terminal_summary(
            sorted_results, self.metrics, top_n=self.config.top_n_results
        )
        return {"metrics": self.metrics, "results": sorted_results}
