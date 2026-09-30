"""
tests/test_input_manager.py
===========================
Unit tests for InputManager (Member 1).

Covers:
- Directory existence and validation
- File discovery matching patterns (only .log/.txt, sorted, no duplicates)
- Total size measurement
- measure_input: file count, bytes and lines
- Input split generation across worker count
- Handling empty/missing directories
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.input_manager import InputManager, InputSplit, create_byte_splits


class TempDirTest(unittest.TestCase):
    """Base class: creates and tears down a temporary directory."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, name: str, text: str) -> Path:
        path = self.tmp / name
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return path


class TestValidateDirectory(TempDirTest):
    """Tests for InputManager.validate_directory()."""

    def test_missing_directory_raises_file_not_found(self):
        """Should raise FileNotFoundError when the target directory does not exist."""
        im = InputManager(self.tmp / "does_not_exist")
        with self.assertRaises(FileNotFoundError):
            im.validate_directory()

    def test_empty_directory_raises_value_error(self):
        """Should raise ValueError when the directory exists but has no log/txt files."""
        im = InputManager(self.tmp)
        with self.assertRaises(ValueError):
            im.validate_directory()

    def test_valid_directory_passes(self):
        """Should not raise when directory contains at least one .log file."""
        self.write("app.log", "ERROR something\n")
        im = InputManager(self.tmp)
        im.validate_directory()  # should not raise


class TestDiscoverFiles(TempDirTest):
    """Tests for InputManager.discover_files()."""

    def test_discovers_only_log_and_txt(self):
        """Should return only .log and .txt files, not .csv or others."""
        self.write("a.log", "x\n")
        self.write("b.txt", "y\n")
        self.write("c.csv", "z\n")
        im = InputManager(self.tmp)
        names = [p.name for p in im.discover_files()]
        self.assertIn("a.log", names)
        self.assertIn("b.txt", names)
        self.assertNotIn("c.csv", names)

    def test_result_is_sorted(self):
        """Discovered files should be returned in sorted order."""
        self.write("c.log", "")
        self.write("a.log", "")
        self.write("b.txt", "")
        im = InputManager(self.tmp)
        names = [p.name for p in im.discover_files()]
        self.assertEqual(names, sorted(names))

    def test_no_duplicates(self):
        """A file matching both *.log and *.txt patterns must not appear twice."""
        # Not possible normally, but guard via unique set check
        self.write("x.log", "line\n")
        self.write("y.txt", "line\n")
        im = InputManager(self.tmp)
        files = im.discover_files()
        self.assertEqual(len(files), len(set(files)))


class TestGetTotalSizeBytes(TempDirTest):
    """Tests for InputManager.get_total_size_bytes()."""

    def test_total_size(self):
        """Should return the sum of file sizes in bytes."""
        p1 = self.write("a.log", "one\ntwo\n")    # 8 bytes
        p2 = self.write("b.log", "three")          # 5 bytes
        im = InputManager(self.tmp)
        total = im.get_total_size_bytes([p1, p2])
        self.assertEqual(total, 13)


class TestMeasureInput(TempDirTest):
    """Tests for InputManager.measure_input()."""

    def test_measure_input(self):
        """3 files: 8 + 5 + 0 = 13 bytes, 2 + 1 + 0 = 3 lines."""
        p1 = self.write("a.log", "one\ntwo\n")   # 2 lines, 8 bytes
        p2 = self.write("b.log", "three")         # 1 line (no newline), 5 bytes
        p3 = self.write("empty.log", "")          # 0 lines, 0 bytes
        im = InputManager(self.tmp)
        stats = im.measure_input([p1, p2, p3])
        self.assertEqual(stats["file_count"], 3)
        self.assertEqual(stats["total_bytes"], 13)
        self.assertEqual(stats["total_lines"], 3)
        self.assertEqual(len(stats["files"]), 3)


class TestCreateSplits(TempDirTest):
    """Tests for InputManager.create_splits()."""

    def test_five_files_two_splits(self):
        """5 files over 2 groups: group sizes should be [3, 2]."""
        files = [self.write(f"f{i}.log", "") for i in range(5)]
        im = InputManager(self.tmp)
        splits = im.create_splits(files, 2)
        self.assertEqual(len(splits), 2)
        self.assertEqual(len(splits[0]), 3)
        self.assertEqual(len(splits[1]), 2)

    def test_zero_splits_raises(self):
        """num_splits=0 should raise ValueError."""
        im = InputManager(self.tmp)
        with self.assertRaises(ValueError):
            im.create_splits([], 0)


class TestByteSplits(TempDirTest):
    """Tests for module-level create_byte_splits()."""

    def test_ranges_for_25_byte_file_size_10(self):
        """25-byte file with split_size=10 → ranges (0,10),(10,20),(20,25) ids 0,1,2."""
        path = self.write("a.log", "x" * 25)
        splits = create_byte_splits([path], split_size=10)
        self.assertEqual(len(splits), 3)
        self.assertEqual([(s.start, s.end) for s in splits],
                         [(0, 10), (10, 20), (20, 25)])
        self.assertEqual([s.split_id for s in splits], [0, 1, 2])

    def test_empty_file_gives_no_splits(self):
        """Empty file should produce no splits."""
        path = self.write("empty.log", "")
        splits = create_byte_splits([path], split_size=10)
        self.assertEqual(splits, [])

    def test_zero_split_size_raises(self):
        """split_size=0 should raise ValueError."""
        with self.assertRaises(ValueError):
            create_byte_splits([], split_size=0)

    def test_split_ids_are_global_sequence(self):
        """split_ids run 0..n-1 across all files."""
        p1 = self.write("a.log", "x" * 15)
        p2 = self.write("b.log", "y" * 10)
        splits = create_byte_splits([p1, p2], split_size=10)
        self.assertEqual([s.split_id for s in splits], list(range(len(splits))))

    def test_length_property(self):
        """InputSplit.length should equal end - start."""
        path = self.write("a.log", "x" * 25)
        splits = create_byte_splits([path], split_size=10)
        for s in splits:
            self.assertEqual(s.length, s.end - s.start)


if __name__ == "__main__":
    unittest.main()
