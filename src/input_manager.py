"""
src/input_manager.py
====================
Input discovery, validation, and data splitting module.

Primary Ownership: Member 1 (Coordinator + Map Phase)

Responsibilities:
- Discover log files in the configured input directory.
- Validate input directory existence and check for empty directories.
- Calculate the total size of input datasets for reporting and performance metrics.
- Partition input files into discrete splits/tasks for assignment to Map workers.
- Handle missing files or unreadable file errors gracefully.
"""

from pathlib import Path
from typing import List, Tuple, Union


class InputManager:
    """Manages input log files, validations, and workload splitting."""

    def __init__(self, input_dir: Path):
        """
        Initialize the InputManager with a target directory.

        :param input_dir: Path to directory containing raw log files.
        """
        self.input_dir = Path(input_dir)

    def validate_directory(self) -> None:
        """
        Validate that the input directory exists and contains files.

        Raises:
            FileNotFoundError: If input directory does not exist.
            ValueError: If input directory contains no readable log files.
        """
        raise NotImplementedError("Member 1 to implement validate_directory logic.")

    def discover_files(self, pattern: str = "*.log") -> List[Path]:
        """
        Scan the input directory and return a list of matching file paths.

        :param pattern: Glob pattern for matching input log files.
        :return: List of Path objects for discovered files.
        """
        raise NotImplementedError("Member 1 to implement discover_files logic.")

    def get_total_size_bytes(self, files: List[Path]) -> int:
        """
        Calculate total file size in bytes across all discovered input files.

        :param files: List of Path objects to measure.
        :return: Total size in bytes.
        """
        raise NotImplementedError("Member 1 to implement get_total_size_bytes logic.")

    def create_splits(self, files: List[Path], num_splits: int) -> List[List[Path]]:
        """
        Divide the discovered input files into splits for parallel map workers.

        :param files: List of Path objects representing input log files.
        :param num_splits: Number of map workers / target partitions.
        :return: List of file lists, where each sublist corresponds to one map worker's task.
        """
        raise NotImplementedError("Member 1 to implement create_splits logic.")
