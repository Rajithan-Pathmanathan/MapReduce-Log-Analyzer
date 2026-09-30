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

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Union

# ---------------------------------------------------------------------------
# Byte-range split (module-level, picklable for multiprocessing)
# ---------------------------------------------------------------------------

DEFAULT_SPLIT_SIZE_BYTES: int = 256 * 1024   # 256 KiB per input split


@dataclass(frozen=True)
class InputSplit:
    """
    A byte-range slice of one input file assigned to a single Map worker.

    Only the file path and offsets are sent to the worker; the worker opens
    the file and reads its own range so the coordinator never ships raw data
    (analogous to a Hadoop split referencing an HDFS block).
    """
    split_id: int
    path: Path
    start: int
    end: int

    @property
    def length(self) -> int:
        """Number of bytes covered by this split."""
        return self.end - self.start


def create_byte_splits(
    files: List[Path],
    split_size: int = DEFAULT_SPLIT_SIZE_BYTES,
) -> List["InputSplit"]:
    """
    Cut every file into byte-range splits of at most `split_size` bytes.

    Empty files produce no splits. `split_id` is a global counter that
    runs 0..n-1 across all files in the order they appear.

    :param files: Sorted list of input file Paths.
    :param split_size: Maximum bytes per split.
    :return: List of InputSplit objects.
    :raises ValueError: If split_size < 1.
    """
    if split_size < 1:
        raise ValueError("split_size must be >= 1")
    splits: List[InputSplit] = []
    for path in files:
        size = path.stat().st_size
        start = 0
        while start < size:
            end = min(start + split_size, size)
            splits.append(InputSplit(
                split_id=len(splits),
                path=path,
                start=start,
                end=end,
            ))
            start = end
    return splits



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
        Validate that the input directory exists and contains .log/.txt files.

        Raises:
            FileNotFoundError: If input directory does not exist.
            NotADirectoryError: If the path exists but is not a directory.
            ValueError: If input directory contains no readable .log/.txt files.
        """
        if not self.input_dir.exists():
            raise FileNotFoundError(
                f"Input directory not found: {self.input_dir}"
            )
        if not self.input_dir.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {self.input_dir}"
            )
        files = self.discover_files()
        if not files:
            raise ValueError(
                f"No .log or .txt files found in: {self.input_dir}"
            )

    def discover_files(
        self, patterns: Tuple[str, ...] = ("*.log", "*.txt")
    ) -> List[Path]:
        """
        Scan the input directory and return a sorted list of matching file paths.
        Duplicates (files matched by multiple patterns) are excluded.

        :param patterns: Glob patterns for matching input log files.
        :return: Sorted list of Path objects for discovered files.
        """
        seen = set()
        files = []
        for pattern in patterns:
            for path in self.input_dir.glob(pattern):
                if path.is_file() and path not in seen:
                    seen.add(path)
                    files.append(path)
        return sorted(files)

    def get_total_size_bytes(self, files: List[Path]) -> int:
        """
        Calculate total file size in bytes across all discovered input files.

        :param files: List of Path objects to measure.
        :return: Total size in bytes.
        """
        return sum(f.stat().st_size for f in files)

    @staticmethod
    def count_lines(path: Path) -> int:
        """
        Count lines in a file by reading in 1 MiB binary blocks.
        A final line without a trailing newline still counts as one line.

        :param path: Path to the file.
        :return: Number of lines in the file.
        """
        lines = 0
        last = b"\n"
        with open(path, "rb") as f:
            while True:
                block = f.read(1 << 20)  # 1 MiB
                if not block:
                    break
                lines += block.count(b"\n")
                last = block[-1:]
        # If the last byte is not a newline the final line has no terminator
        if last != b"\n":
            lines += 1
        return lines

    def measure_input(self, files: List[Path]) -> dict:
        """
        Measure the real size of the input. Nothing here is estimated.

        :param files: List of Path objects to measure.
        :return: Dict with keys: file_count, total_bytes, total_lines, files
                 where 'files' is a list of per-file dicts
                 {file: str, bytes: int, lines: int}.
        """
        per_file = []
        for path in files:
            per_file.append({
                "file": path.name,
                "bytes": path.stat().st_size,
                "lines": self.count_lines(path),
            })
        return {
            "file_count": len(per_file),
            "total_bytes": sum(p["bytes"] for p in per_file),
            "total_lines": sum(p["lines"] for p in per_file),
            "files": per_file,
        }

    def create_splits(self, files: List[Path], num_splits: int) -> List[List[Path]]:
        """
        Divide the discovered input files into splits for parallel map workers
        using round-robin assignment.

        Note: The coordinator now uses byte-range splits (create_byte_splits).
        This method keeps the original file-group interface for backward
        compatibility.

        :param files: List of Path objects representing input log files.
        :param num_splits: Number of map workers / target partitions.
        :return: List of file lists, each sublist is one map worker's task.
        :raises ValueError: If num_splits < 1.
        """
        if num_splits < 1:
            raise ValueError("num_splits must be >= 1")
        splits: List[List[Path]] = [[] for _ in range(num_splits)]
        for i, f in enumerate(files):
            splits[i % num_splits].append(f)
        return splits
