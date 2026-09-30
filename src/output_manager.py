"""
src/output_manager.py
=====================
Result aggregation formatting, file writing, and execution summary module.

Primary Ownership: Member 3 (Integration + Testing + Documentation)

Responsibilities:
- Consolidate reduced key-value tuples from all reduce workers into a unified dataset.
- Sort results in descending order of frequency (Top-N items).
- Write formatted results to the designated output file (e.g., output/result.txt).
- Display a clean, professional console report detailing input files, data size,
  worker concurrency settings, phase timings, and top event counts (suitable for
  the academic report's Figure 7 screenshot).
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple


class OutputManager:
    """Manages sorting, formatting, and file export of MapReduce results."""

    def __init__(self, output_dir: Path, output_file_name: str = "result.txt"):
        """
        Initialize the OutputManager.

        :param output_dir: Directory where result files are stored.
        :param output_file_name: Name of the summary text file.
        """
        self.output_dir = Path(output_dir)
        self.output_file = self.output_dir / output_file_name

    def consolidate_and_sort(
        self, reducer_results: List[List[Tuple[str, int]]]
    ) -> List[Tuple[str, int]]:
        """
        Combine outputs from all reducers and sort by frequency in descending order.
        Secondary sort is alphabetical by key for deterministic results.

        :param reducer_results: List containing results from each reduce worker.
        :return: Flattened, sorted list of (key, total_count) tuples.
        """
        combined: List[Tuple[str, int]] = []
        for worker_res in reducer_results:
            combined.extend(worker_res)

        # Sort descending by count, then ascending by key
        combined.sort(key=lambda item: (-item[1], item[0]))
        return combined

    def write_output_file(
        self,
        sorted_results: List[Tuple[str, int]],
        metrics: Dict[str, Any],
        custom_path: Path = None,
    ) -> Path:
        """
        Write the analysis results and execution metrics to a persistent file.

        :param sorted_results: Sorted list of (key, count) tuples.
        :param metrics: Dictionary of performance and execution metadata.
        :param custom_path: Optional custom file path override.
        :return: Path to the generated output file.
        """
        target_path = custom_path if custom_path else self.output_file
        target_path.parent.mkdir(parents=True, exist_ok=True)

        size_mb = metrics.get("total_input_bytes", 0) / (1024 * 1024)
        exec_time = metrics.get("total_execution_time_seconds", 0.0)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write("MapReduce Log Analysis Results\n")
            f.write("==============================\n\n")
            f.write(f"Input Files    : {metrics.get('input_files_count', 0)}\n")
            f.write(f"Input Size     : {size_mb:.4f} MB ({metrics.get('total_input_bytes', 0):,} bytes)\n")
            f.write(f"Map Workers    : {metrics.get('map_workers', 1)}\n")
            f.write(f"Reduce Workers : {metrics.get('reduce_workers', 1)}\n")
            f.write(f"Input Lines    : {metrics.get('total_input_lines', 0):,}\n")
            f.write(f"Input Splits   : {metrics.get('input_splits', 0)}\n")
            f.write(f"Map Output     : {metrics.get('intermediate_pairs', 0):,} (term, 1) pairs\n")
            f.write(f"Unique Keys    : {len(sorted_results)}\n")
            f.write(f"Keys/Reducer   : {metrics.get('keys_per_reducer', [])}\n")
            f.write(f"Execution Time : {exec_time:.4f} seconds\n\n")

            f.write("Phase Breakdown\n")
            f.write("---------------\n")
            f.write(f"Map Phase      : {metrics.get('map_time_seconds', 0.0):.4f} seconds\n")
            f.write(f"Shuffle Phase  : {metrics.get('shuffle_time_seconds', 0.0):.4f} seconds\n")
            f.write(f"Reduce Phase   : {metrics.get('reduce_time_seconds', 0.0):.4f} seconds\n\n")

            f.write("Top Results\n")
            f.write("-----------\n")
            for key, count in sorted_results[: metrics.get("top_n", 20)]:
                f.write(f"{key:<20} {count:>8}\n")

        return target_path

    def display_terminal_summary(
        self,
        sorted_results: List[Tuple[str, int]],
        metrics: Dict[str, Any],
        top_n: int = 10,
    ) -> None:
        """
        Print a formatted execution summary to the terminal.
        Designed to provide clear visual validation for university report screenshots.

        :param sorted_results: Sorted list of (key, count) tuples.
        :param metrics: Execution statistics (file count, size, workers, timing).
        :param top_n: Number of top results to display.
        """
        size_mb = metrics.get("total_input_bytes", 0) / (1024 * 1024)
        total_time = metrics.get("total_execution_time_seconds", 0.0)

        print("\n" + "=" * 60)
        print("          MAPREDUCE LOG ANALYSIS EXECUTION SUMMARY          ")
        print("=" * 60)
        print(f" Input Files Detected : {metrics.get('input_files_count', 0)}")
        print(f" Total Input Size     : {size_mb:.4f} MB ({metrics.get('total_input_bytes', 0):,} bytes)")
        print(f" Map Workers          : {metrics.get('map_workers', 1)}")
        print(f" Reduce Workers       : {metrics.get('reduce_workers', 1)}")
        print(f" Input Lines          : {metrics.get('total_input_lines', 0):,}")
        print(f" Input Splits         : {metrics.get('input_splits', 0)}")
        print(f" Map Output Pairs     : {metrics.get('intermediate_pairs', 0):,}")
        print(f" Total Unique Keys    : {len(sorted_results)}")
        print(f" Keys per Reducer     : {metrics.get('keys_per_reducer', [])}")
        print(f" Total Execution Time : {total_time:.4f} seconds")
        print("-" * 60)
        print(" Stage Timing Breakdown:")
        print(f"   - Map Phase        : {metrics.get('map_time_seconds', 0.0):.4f} s")
        print(f"   - Shuffle Phase    : {metrics.get('shuffle_time_seconds', 0.0):.4f} s")
        print(f"   - Reduce Phase     : {metrics.get('reduce_time_seconds', 0.0):.4f} s")
        print("-" * 60)
        print(f" Top {min(top_n, len(sorted_results))} Event / Token Counts:")
        print(f" {'TERM / EVENT':<25} {'COUNT':>10}")
        print(" " + "-" * 37)
        for key, count in sorted_results[:top_n]:
            print(f" {key:<25} {count:>10,}")
        print("=" * 60 + "\n")
