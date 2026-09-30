"""
src/mapper.py
=============
Map worker and log tokenization module.

Primary Ownership: Member 1 (Coordinator + Map Phase)

Responsibilities:
- Process an assigned input split (one or more log files).
- Parse and tokenize raw log lines into clean tokens/terms.
- Emit intermediate key-value pairs: List of tuples (token: str, 1: int).
- Measure execution time for the map stage.

Tokenisation rules:
  1. By default the line is lowercased before matching (case_sensitive=False).
  2. A token MUST start with a letter at a word boundary
     (negative look-behind for [a-z0-9_-]).
     This means pure numbers (timestamps, IP octets, ports), strings like
     "000z", "192", "168" or "2026-09-30t14" are NOT counted as tokens.
  3. After the leading letter, digits, underscores and hyphens are allowed
     so identifiers like "db_pool", "http2", "payment-gateway" are kept.
  4. Tokens shorter than min_word_length are dropped.

Example:
  "2026-09-30T14:02:11.000Z 192.168.1.10 INFO payment-gateway 200 OK"
  -> [("info", 1), ("payment-gateway", 1), ("ok", 1)]
"""

import os
import re
import time
from pathlib import Path
from typing import List, Tuple

# Matches a token that starts with a letter (not preceded by a-z, 0-9, _ or -)
TOKEN_PATTERN = re.compile(r"(?<![a-z0-9_-])[a-z][a-z0-9_-]*")
TOKEN_PATTERN_CASED = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z][A-Za-z0-9_-]*")


def tokenize_log_line(
    line: str,
    case_sensitive: bool = False,
    min_word_length: int = 2,
) -> List[str]:
    """
    Parse a single log line into normalized tokens.

    Returns an empty list for blank or whitespace-only lines.

    :param line: Raw text line from a log file.
    :param case_sensitive: When False (default), line is lowercased first.
    :param min_word_length: Drop tokens shorter than this length.
    :return: List of clean string tokens extracted from the line.
    """
    if not line.strip():
        return []
    if case_sensitive:
        tokens = TOKEN_PATTERN_CASED.findall(line)
    else:
        tokens = TOKEN_PATTERN.findall(line.lower())
    return [t for t in tokens if len(t) >= min_word_length]


def map_function(
    line: str,
    case_sensitive: bool = False,
    min_word_length: int = 2,
) -> List[Tuple[str, int]]:
    """
    The user-defined Map function: one log line -> list of (term, 1) pairs.

    :param line: Raw text line from a log file.
    :param case_sensitive: Preserve original casing when True.
    :param min_word_length: Minimum token length to emit.
    :return: List of (token, 1) intermediate pairs.
    """
    return [(term, 1) for term in tokenize_log_line(line, case_sensitive, min_word_length)]


def map_worker(
    split_files: List[Path],
    worker_id: int,
    case_sensitive: bool = False,
    min_word_length: int = 2,
) -> List[Tuple[str, int]]:
    """
    Map worker process function executed in parallel.

    Reads assigned log files and emits a list of intermediate (key, value) pairs.
    Skips missing files gracefully; prints a warning on OSError and continues.

    :param split_files: List of file paths assigned to this map worker.
    :param worker_id: Numeric identifier for the worker process.
    :param case_sensitive: Whether tokenization preserves casing.
    :param min_word_length: Minimum token length to emit.
    :return: List of intermediate (key, value) pairs, e.g. [("error", 1), ...].
    """
    pairs: List[Tuple[str, int]] = []
    for path in split_files:
        path = Path(path)
        if not path.exists():
            print(f"[Map worker {worker_id}] WARNING: file not found, skipping: {path}")
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    pairs.extend(map_function(line, case_sensitive, min_word_length))
        except OSError as exc:
            print(f"[Map worker {worker_id}] WARNING: {exc}, skipping: {path}")
    return pairs


# ---------------------------------------------------------------------------
# Byte-range reading (Step 5)
# ---------------------------------------------------------------------------

def read_split_lines(path, start: int, end: int):
    """
    Yield the decoded lines that belong to the byte range [start, end) of a file.

    Line-boundary rule (same as Hadoop's LineRecordReader):
      - A split OWNS every line whose FIRST BYTE lies inside [start, end).
      - If start > 0, seek to (start-1) and discard the partial line
        (it belongs to the previous split).
      - Reading continues while the current line's first byte is < end;
        the last line may extend past end and is still included.

    :param path: Path to the file.
    :param start: First byte of the split (inclusive).
    :param end: One past the last byte of the split.
    :yields: Decoded text lines (UTF-8, errors replaced).
    """
    with open(path, "rb") as f:
        if start > 0:
            f.seek(start - 1)
            f.readline()          # skip partial line belonging to previous split
        pos = f.tell()
        while pos < end:
            raw = f.readline()
            if not raw:
                break
            pos += len(raw)
            yield raw.decode("utf-8", errors="replace")


def map_split_worker(
    split,
    case_sensitive: bool = False,
    min_word_length: int = 2,
) -> dict:
    """
    Entry point executed inside a worker process for one InputSplit.

    Accepts either an InputSplit dataclass or a plain dict with the same
    fields (split_id, path, start, end) for pickling compatibility.

    Returns:
        {
            "split_id":   int,
            "worker_pid": int,
            "lines":      int,
            "pairs":      List[Tuple[str, int]],
            "elapsed":    float,   # seconds (perf_counter)
        }
    """
    t0 = time.perf_counter()
    # Accept both InputSplit dataclass and plain dict
    if hasattr(split, "split_id"):
        split_id, path, start, end = split.split_id, split.path, split.start, split.end
    else:
        split_id, path, start, end = (
            split["split_id"], split["path"], split["start"], split["end"]
        )

    pairs = []
    lines = 0
    for line in read_split_lines(path, start, end):
        lines += 1
        pairs.extend(map_function(line, case_sensitive, min_word_length))

    return {
        "split_id": split_id,
        "worker_pid": os.getpid(),
        "lines": lines,
        "pairs": pairs,
        "elapsed": time.perf_counter() - t0,
    }
