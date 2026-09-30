"""
tests/test_input_manager.py
===========================
Unit tests for InputManager (Member 1).

Covers:
- Directory existence and validation
- File discovery matching patterns
- Input split generation across worker count
- Handling empty/missing directories
"""

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.input_manager import InputManager


class TestInputManager(unittest.TestCase):
    """Test suite for input discovery, validation, and splitting."""

    def setUp(self):
        """Create a temporary directory for isolated file operations."""
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir_obj.name)
        self.input_manager = InputManager(self.test_dir)

    def tearDown(self):
        """Clean up temporary test directory."""
        self.temp_dir_obj.cleanup()

    def test_validate_directory_missing(self):
        """Should raise FileNotFoundError when the target directory does not exist."""
        non_existent_dir = self.test_dir / "does_not_exist"
        mgr = InputManager(non_existent_dir)
        with self.assertRaises(FileNotFoundError):
            mgr.validate_directory()

    def test_validate_directory_empty(self):
        """Should raise ValueError when directory exists but has no log files."""
        with self.assertRaises(ValueError):
            self.input_manager.validate_directory()

    def test_discover_files(self):
        """Should return all matching log files in sorted order."""
        f1 = self.test_dir / "server_b.log"
        f2 = self.test_dir / "server_a.log"
        f3 = self.test_dir / "notes.txt"
        f4 = self.test_dir / "ignore.csv"

        for f in (f1, f2, f3, f4):
            f.write_text("sample content", encoding="utf-8")

        discovered = self.input_manager.discover_files()
        file_names = [f.name for f in discovered]

        self.assertIn("server_a.log", file_names)
        self.assertIn("server_b.log", file_names)
        self.assertIn("notes.txt", file_names)
        self.assertNotIn("ignore.csv", file_names)
        self.assertEqual(len(discovered), 3)

    def test_get_total_size_bytes(self):
        """Should correctly sum the byte size of discovered files."""
        f1 = self.test_dir / "log1.log"
        f2 = self.test_dir / "log2.log"
        f1.write_text("12345", encoding="utf-8")  # 5 bytes
        f2.write_text("1234567890", encoding="utf-8")  # 10 bytes

        files = [f1, f2]
        total_size = self.input_manager.get_total_size_bytes(files)
        self.assertEqual(total_size, 15)

    def test_create_splits(self):
        """Should divide files into balanced subsets equal to the split count."""
        files = [self.test_dir / f"log_{i}.log" for i in range(5)]
        for f in files:
            f.write_text("test", encoding="utf-8")

        splits = self.input_manager.create_splits(files, num_splits=2)
        self.assertEqual(len(splits), 2)
        # 5 files across 2 splits: 3 files in split 0, 2 files in split 1
        self.assertEqual(len(splits[0]), 3)
        self.assertEqual(len(splits[1]), 2)

    def test_create_splits_invalid_workers(self):
        """Should raise ValueError if split count is less than 1."""
        with self.assertRaises(ValueError):
            self.input_manager.create_splits([], num_splits=0)


if __name__ == "__main__":
    unittest.main()
