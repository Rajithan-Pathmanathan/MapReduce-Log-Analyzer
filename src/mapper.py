"""
src/mapper.py
=============
Map worker and log tokenization module.

Primary Ownership: Member 1 (Coordinator + Map Phase)

Responsibilities:
- Process an assigned input split (one or more log files).
- Parse and tokenize raw log lines into clean tokens/terms (e.g., lowercase, stripped punctuation).
- Emit intermediate key-value pairs: List of tuples (token: str, 1: int).
- Handle empty files and whitespace lines cleanly without crashing.

Example Conceptual Output:
    [
        ("error", 1),
        ("database", 1),
        ("connection", 1),
        ("failed", 1)
    ]
"""

import re
from pathlib import Path
from typing import List, Tuple

# Token extraction pattern: alphanumeric words, hyphens, and underscores
TOKEN_PATTERN = re.compile(r"\b[a-zA-Z0-9_-]+\b")


def tokenize_log_line(
    line: str, case_sensitive: bool = False, min_word_length: int = 2
) -> List[str]:
    """
    Parse a single log line into normalized tokens.

    :param line: Raw text line from a log file.
    :param case_sensitive: Whether tokenization preserves casing.
    :param min_word_length: Minimum character length for tokens.
    :return: List of clean string tokens extracted from the line.
    """
    if not line or not line.strip():
        return []

    processed_line = line if case_sensitive else line.lower()
    raw_tokens = TOKEN_PATTERN.findall(processed_line)

    # Filter out tokens shorter than threshold
    return [token for token in raw_tokens if len(token) >= min_word_length]


def map_worker(split_files: List[Path], worker_id: int) -> List[Tuple[str, int]]:
    """
    Map worker process function executed in parallel.
    Reads assigned log files and emits a list of intermediate key-value pairs.

    :param split_files: List of file paths assigned to this map worker.
    :param worker_id: Numeric identifier for the worker process.
    :return: List of intermediate (key, value) pairs, e.g. [("error", 1), ...].
    """
    intermediate_pairs: List[Tuple[str, int]] = []

    for file_path in split_files:
        path_obj = Path(file_path)
        if not path_obj.exists() or not path_obj.is_file():
            continue

        try:
            with open(path_obj, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    tokens = tokenize_log_line(line)
                    for token in tokens:
                        intermediate_pairs.append((token, 1))
        except Exception as exc:
            print(f"[Worker {worker_id}] Warning: Error reading file '{path_obj}': {exc}")

    return intermediate_pairs
