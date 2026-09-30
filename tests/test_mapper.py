"""
tests/test_mapper.py
====================
Unit tests for Mapper module (Member 1).

Covers:
- Token extraction and normalization (lowercasing, punctuation stripping)
- Generation of (key, 1) intermediate tuples
- Handling empty log lines or whitespace
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mapper import tokenize_log_line, map_worker


class TestMapper(unittest.TestCase):
    """Test suite for log tokenization and Map worker transformation."""

    def test_tokenize_log_line_normalization(self):
        """Should convert tokens to lowercase and strip unwanted characters."""
        # Scaffolding placeholder for Member 1
        # Example test case to implement:
        # line = "ERROR Database connection failed!"
        # tokens = tokenize_log_line(line)
        # self.assertEqual(tokens, ["error", "database", "connection", "failed"])
        pass

    def test_tokenize_empty_line(self):
        """Should return an empty list for blank or whitespace-only lines."""
        # Scaffolding placeholder for Member 1
        pass

    def test_map_worker_output_format(self):
        """Should emit a list of (token, 1) tuples from input files."""
        # Scaffolding placeholder for Member 1
        pass


if __name__ == "__main__":
    unittest.main()
