"""
tests/test_mapper.py
====================
Unit tests for Mapper module (Member 1).

Covers:
- Token extraction: leading-letter rule blocks numeric noise (IPs, timestamps)
- Lowercase normalisation and punctuation stripping
- case_sensitive and min_word_length parameters
- Blank / whitespace-only lines -> empty list
- map_function emits (term, 1) pairs
- map_worker on normal files, empty files and missing files
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mapper import tokenize_log_line, map_function, map_worker


class TestTokenizeLogLine(unittest.TestCase):
    """Tests for tokenize_log_line()."""

    def test_basic_error_line(self):
        """Four plain words -> four tokens."""
        self.assertEqual(
            tokenize_log_line("ERROR database connection failed"),
            ["error", "database", "connection", "failed"],
        )

    def test_punctuation_and_brackets(self):
        """Punctuation and brackets act as separators; code=500 keeps 'code'."""
        result = tokenize_log_line("ERROR Database connection failed! [code=500]")
        self.assertEqual(result, ["error", "database", "connection", "failed", "code"])

    def test_numeric_noise_dropped(self):
        """Timestamps, IP octets and pure numbers must NOT appear as tokens."""
        result = tokenize_log_line(
            "2026-09-30T14:02:11.000Z 192.168.1.10 INFO payment-gateway 200 OK"
        )
        self.assertNotIn("2026", result)
        self.assertNotIn("192", result)
        self.assertNotIn("168", result)
        self.assertNotIn("000z", result)
        self.assertIn("info", result)
        self.assertIn("payment-gateway", result)
        self.assertIn("ok", result)

    def test_identifiers_with_digits_and_underscores(self):
        """Tokens starting with a letter that contain digits/underscores are kept."""
        result = tokenize_log_line("user_42 http2 inventory-api")
        self.assertIn("user_42", result)
        self.assertIn("http2", result)
        self.assertIn("inventory-api", result)

    def test_min_word_length_default(self):
        """Default min_word_length=2: single-letter 'a' is dropped."""
        result = tokenize_log_line("A is an error")
        self.assertNotIn("a", result)
        self.assertIn("is", result)
        self.assertIn("an", result)
        self.assertIn("error", result)

    def test_min_word_length_three(self):
        """min_word_length=3: only 'error' survives from 'A is an error'."""
        result = tokenize_log_line("A is an error", min_word_length=3)
        self.assertEqual(result, ["error"])

    def test_case_sensitive_true(self):
        """case_sensitive=True preserves original casing."""
        result = tokenize_log_line("ERROR Error error", case_sensitive=True)
        self.assertIn("ERROR", result)
        self.assertIn("Error", result)
        self.assertIn("error", result)

    def test_blank_line_returns_empty(self):
        """Blank line -> []."""
        self.assertEqual(tokenize_log_line(""), [])

    def test_whitespace_only_returns_empty(self):
        """Whitespace-only line -> []."""
        self.assertEqual(tokenize_log_line("   \t\n"), [])


class TestMapFunction(unittest.TestCase):
    """Tests for map_function()."""

    def test_emits_term_one_pairs(self):
        """Each token should be paired with value 1."""
        result = map_function("ERROR database connection failed")
        self.assertEqual(
            result,
            [("error", 1), ("database", 1), ("connection", 1), ("failed", 1)],
        )

    def test_empty_line_returns_empty(self):
        """Empty line -> no pairs."""
        self.assertEqual(map_function(""), [])


class TestMapWorker(unittest.TestCase):
    """Tests for map_worker()."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, name, text):
        p = self.tmp / name
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return p

    def test_normal_file(self):
        """map_worker reads a normal file and returns (token, 1) pairs."""
        p = self.write("a.log", "ERROR database\n")
        result = map_worker([p], worker_id=0)
        self.assertIn(("error", 1), result)
        self.assertIn(("database", 1), result)

    def test_empty_file(self):
        """map_worker on an empty file returns []."""
        p = self.write("empty.log", "")
        self.assertEqual(map_worker([p], worker_id=0), [])

    def test_missing_file_skipped(self):
        """map_worker skips a missing file and does not raise."""
        missing = self.tmp / "ghost.log"
        result = map_worker([missing], worker_id=0)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
