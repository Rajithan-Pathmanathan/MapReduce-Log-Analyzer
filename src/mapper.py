"""
src/mapper.py
=============
Map worker and log tokenization module.

Primary Ownership: Member 1 (Coordinator + Map Phase)

Responsibilities:
- Process an assigned input split (one or more log files).
- Parse and tokenize raw log lines into clean tokens/terms (e.g., lowercase, stripped punctuation).
- Emit intermediate key-value pairs: List of tuples (token: str, 1: int).
- Measure execution time for the map stage.

Example Conceptual Output:
    [
        ("error", 1),
        ("database", 1),
        ("connection", 1),
        ("failed", 1)
    ]
"""

from pathlib import Path
from typing import List, Tuple


def tokenize_log_line(line: str, case_sensitive: bool = False) -> List[str]:
    """
    Parse a single log line into normalized tokens.

    :param line: Raw text line from a log file.
    :param case_sensitive: Whether tokenization preserves casing.
    :return: List of clean string tokens extracted from the line.
    """
    raise NotImplementedError("Member 1 to implement tokenize_log_line.")


def map_worker(split_files: List[Path], worker_id: int) -> List[Tuple[str, int]]:
    """
    Map worker process function executed in parallel.
    Reads assigned log files and emits a list of intermediate key-value pairs.

    :param split_files: List of file paths assigned to this map worker.
    :param worker_id: Numeric identifier for the worker process.
    :return: List of intermediate (key, value) pairs, e.g. [("error", 1), ...].
    """
    raise NotImplementedError("Member 1 to implement map_worker.")
