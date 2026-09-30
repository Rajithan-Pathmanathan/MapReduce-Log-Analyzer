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

import os
from pathlib import Path
from typing import List, Sequence


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
        Validate that the input directory exists and contains accessible files.

        Raises:
            FileNotFoundError: If input directory does not exist.
            ValueError: If input directory contains no readable log files.
        """
        if not self.input_dir.exists():
            raise FileNotFoundError(
                f"Input directory does not exist: {self.input_dir.resolve()}"
            )
        if not self.input_dir.is_dir():
            raise NotADirectoryError(
                f"Configured input path is not a directory: {self.input_dir.resolve()}"
            )

        files = self.discover_files()
        if not files:
            raise ValueError(
                f"Input directory '{self.input_dir.resolve()}' contains no readable .log or .txt files."
            )

    def discover_files(self, patterns: Sequence[str] = ("*.log", "*.txt")) -> List[Path]:
        """
        Scan the input directory and return a sorted list of matching file paths.

        :param patterns: Sequence of glob patterns for matching input files.
        :return: Sorted list of Path objects for discovered files.
        """
        if not self.input_dir.exists() or not self.input_dir.is_dir():
            return []

        discovered: List[Path] = []
        for pattern in patterns:
            discovered.extend(self.input_dir.glob(pattern))

        # Filter out directories if any match pattern, and sort for deterministic ordering
        return sorted([f for f in discovered if f.is_file()])

    def get_total_size_bytes(self, files: List[Path]) -> int:
        """
        Calculate total file size in bytes across all discovered input files.

        :param files: List of Path objects to measure.
        :return: Total size in bytes.
        """
        total = 0
        for f in files:
            if f.exists() and f.is_file():
                total += f.stat().st_size
        return total

    def create_splits(self, files: List[Path], num_splits: int) -> List[List[Path]]:
        """
        Divide the discovered input files into splits for parallel map workers.
        Uses round-robin allocation to balance file count per worker.

        :param files: List of Path objects representing input log files.
        :param num_splits: Number of map workers / target partitions.
        :return: List of file lists, where each sublist corresponds to one map worker's task.
        """
        if num_splits < 1:
            raise ValueError(f"Number of splits must be >= 1, received: {num_splits}")

        splits: List[List[Path]] = [[] for _ in range(num_splits)]
        if not files:
            return splits

        for index, file_path in enumerate(files):
            splits[index % num_splits].append(file_path)

        return splits
