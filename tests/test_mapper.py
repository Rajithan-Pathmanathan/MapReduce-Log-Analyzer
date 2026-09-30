"""
tests/test_mapper.py
====================
Unit tests for Mapper module (Member 1).

Covers:
- Token extraction and normalization (lowercasing, punctuation stripping)
- Generation of (key, 1) intermediate tuples
- Handling empty log lines or whitespace
- Handling empty files without errors
"""

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mapper import map_worker, tokenize_log_line


class TestMapper(unittest.TestCase):
    """Test suite for log tokenization and Map worker transformation."""

    def test_tokenize_log_line_normalization(self):
        """Should convert tokens to lowercase and strip punctuation and symbols."""
        line = "ERROR Database connection failed! [code=500]"
        tokens = tokenize_log_line(line)
        self.assertEqual(tokens, ["error", "database", "connection", "failed", "code", "500"])

    def test_tokenize_empty_and_whitespace_lines(self):
        """Should return an empty list for blank or whitespace-only lines."""
        self.assertEqual(tokenize_log_line(""), [])
        self.assertEqual(tokenize_log_line("    \t \n"), [])

    def test_tokenize_filter_short_tokens(self):
        """Tokens shorter than min_word_length should be excluded."""
        line = "A is an error"
        tokens = tokenize_log_line(line, min_word_length=2)
        self.assertEqual(tokens, ["is", "an", "error"])

    def test_map_worker_output_format(self):
        """Should emit a list of (token, 1) tuples from an assigned file."""
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".log") as tmp:
            tmp.write("ERROR Database ERROR\n")
            tmp_path = Path(tmp.name)

        try:
            pairs = map_worker([tmp_path], worker_id=0)
            self.assertEqual(
                pairs,
                [("error", 1), ("database", 1), ("error", 1)],
            )
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_map_worker_empty_file(self):
        """Should return an empty list when processing an empty file."""
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".log") as tmp:
            tmp.write("")
            tmp_path = Path(tmp.name)

        try:
            pairs = map_worker([tmp_path], worker_id=0)
            self.assertEqual(pairs, [])
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
