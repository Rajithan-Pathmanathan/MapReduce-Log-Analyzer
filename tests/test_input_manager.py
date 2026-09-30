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
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.input_manager import InputManager


class TestInputManager(unittest.TestCase):
    """Test suite for input discovery, validation, and splitting."""

    def setUp(self):
        """Set up test environment and mock paths."""
        self.test_dir = Path("input")
        self.input_manager = InputManager(self.test_dir)

    def test_validate_directory_missing(self):
        """Should raise FileNotFoundError when the target directory does not exist."""
        # Scaffolding placeholder for Member 1
        pass

    def test_discover_files(self):
        """Should return all matching log files in the directory."""
        # Scaffolding placeholder for Member 1
        pass

    def test_create_splits(self):
        """Should divide files into balanced subsets equal to the split count."""
        # Scaffolding placeholder for Member 1
        pass


if __name__ == "__main__":
    unittest.main()
