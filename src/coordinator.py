"""
src/coordinator.py
==================
MapReduce job execution coordinator and pipeline orchestrator.

Primary Ownership: Member 1 (Coordinator + Map Phase)
Integration Lead: Member 3 (Integration + Testing + Documentation)

Responsibilities:
- Coordinate the lifecycle of a complete MapReduce job.
- Validate inputs and initialize input file splits via InputManager.
- Spawn and manage parallel Map worker processes using Python multiprocessing.
- Collect intermediate key-value results from Map workers.
- Hand over intermediate results to ShuffleManager (Member 2) for grouping and partitioning.
- Spawn and manage parallel Reduce worker processes using Python multiprocessing.
- Collect and pass reduced partitions to OutputManager (Member 3).
- Measure wall-clock execution time for individual phases and total runtime.
"""

import multiprocessing
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
from src.config import Config
from src.input_manager import InputManager
from src.mapper import map_worker
from src.output_manager import OutputManager
from src.reducer import reduce_worker
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
            "map_workers": config.map_workers,
            "reduce_workers": config.reduce_workers,
            "unique_keys": 0,
            "map_time_seconds": 0.0,
            "shuffle_time_seconds": 0.0,
            "reduce_time_seconds": 0.0,
            "total_execution_time_seconds": 0.0,
            "top_n": config.top_n_results,
        }

    def run_map_phase(self, splits: List[List[Path]]) -> List[Tuple[str, int]]:
        """
        Launch parallel Map worker processes to process input splits.

        :param splits: Grouped input file paths for each Map worker.
        :return: Flattened list of all emitted (key, value) pairs.
        """
        num_workers = min(self.config.map_workers, max(1, len(splits)))
        tasks = [(split, worker_id) for worker_id, split in enumerate(splits)]

        with multiprocessing.Pool(processes=num_workers) as pool:
            worker_outputs = pool.starmap(map_worker, tasks)

        flattened_pairs: List[Tuple[str, int]] = []
        for pairs in worker_outputs:
            flattened_pairs.extend(pairs)

        return flattened_pairs

    def run_reduce_phase(
        self, partitions: Dict[int, Dict[str, List[int]]]
    ) -> List[List[Tuple[str, int]]]:
        """
        Launch parallel Reduce worker processes to aggregate partitioned data.

        :param partitions: Mapping from reducer ID to partition payload.
        :return: List of results collected from each reduce worker.
        """
        num_workers = min(self.config.reduce_workers, max(1, len(partitions)))
        tasks = [
            (partitions.get(r_id, {}), r_id)
            for r_id in range(self.config.reduce_workers)
        ]

        with multiprocessing.Pool(processes=num_workers) as pool:
            reducer_outputs = pool.starmap(reduce_worker, tasks)

        return reducer_outputs

    def execute_job(self) -> Dict[str, Any]:
        """
        Execute the end-to-end MapReduce job pipeline:
        1. Discover & validate input files
        2. Create input splits
        3. Parallel Map phase
        4. Shuffle & Partition phase
        5. Parallel Reduce phase
        6. Consolidate results & output summary

        :return: Execution summary dictionary including metrics and sorted results.
        """
        job_start_time = time.perf_counter()

        # Step 1: Input discovery & validation
        self.input_manager.validate_directory()
        files = self.input_manager.discover_files()
        total_size = self.input_manager.get_total_size_bytes(files)

        self.metrics["input_files_count"] = len(files)
        self.metrics["total_input_bytes"] = total_size

        splits = self.input_manager.create_splits(files, self.config.map_workers)

        # Step 2: Map Phase
        map_start = time.perf_counter()
        intermediate_pairs = self.run_map_phase(splits)
        self.metrics["map_time_seconds"] = time.perf_counter() - map_start

        # Step 3: Shuffle & Partition Phase
        shuffle_start = time.perf_counter()
        partitions = self.shuffle_manager.shuffle_and_partition(intermediate_pairs)
        self.metrics["shuffle_time_seconds"] = time.perf_counter() - shuffle_start

        # Step 4: Reduce Phase
        reduce_start = time.perf_counter()
        reducer_results = self.run_reduce_phase(partitions)
        self.metrics["reduce_time_seconds"] = time.perf_counter() - reduce_start

        # Step 5: Output Consolidation & Reporting
        sorted_results = self.output_manager.consolidate_and_sort(reducer_results)
        self.metrics["unique_keys"] = len(sorted_results)
        self.metrics["total_execution_time_seconds"] = time.perf_counter() - job_start_time

        # Write output file and display terminal report
        self.output_manager.write_output_file(sorted_results, self.metrics)
        self.output_manager.display_terminal_summary(
            sorted_results, self.metrics, top_n=self.config.top_n_results
        )

        return {"metrics": self.metrics, "results": sorted_results}
