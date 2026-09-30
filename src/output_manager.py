"""
src/output_manager.py
=====================
Result aggregation formatting, file writing, and execution summary module.

Primary Ownership: Member 3 (Integration + Testing + Documentation)

Responsibilities:
- Consolidate reduced key-value tuples from all reduce workers into a unified dataset.
- Sort results in descending order of frequency (Top-N items).
- Write formatted results to the designated output file (output/analysis_summary.txt).
- Display a clean, professional console report detailing input files, data size,
  worker concurrency settings, phase timings, and top event counts (suitable for
  the academic report's Figure 7 screenshot).
"""

from pathlib import Path
from typing import Dict, List, Tuple


class OutputManager:
    """Manages sorting, formatting, and file export of MapReduce results."""

    def __init__(self, output_dir: Path, output_file_name: str = "analysis_summary.txt"):
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

        :param reducer_results: List containing results from each reduce worker.
        :return: Flattened, sorted list of (key, total_count) tuples.
        """
        raise NotImplementedError("Member 3 to implement consolidate_and_sort.")

    def write_output_file(
        self,
        sorted_results: List[Tuple[str, int]],
        metrics: Dict[str, object],
    ) -> Path:
        """
        Write the analysis results and execution metrics to a persistent file.

        :param sorted_results: Sorted list of (key, count) tuples.
        :param metrics: Dictionary of performance and execution metadata.
        :return: Path to the generated output file.
        """
        raise NotImplementedError("Member 3 to implement write_output_file.")

    def display_terminal_summary(
        self,
        sorted_results: List[Tuple[str, int]],
        metrics: Dict[str, object],
        top_n: int = 10,
    ) -> None:
        """
        Print a formatted execution summary to the terminal.
        Designed to provide clear visual validation for university report screenshots.

        :param sorted_results: Sorted list of (key, count) tuples.
        :param metrics: Execution statistics (file count, size, workers, timing).
        :param top_n: Number of top results to display.
        """
        raise NotImplementedError("Member 3 to implement display_terminal_summary.")
