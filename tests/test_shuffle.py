"""
tests/test_shuffle.py
=====================
Unit tests for ShuffleManager (Member 2).

Covers:
- Grouping flat intermediate pairs by unique key
- Distribution of grouped keys into reducer-specific partitions
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shuffle import ShuffleManager


class TestShuffleManager(unittest.TestCase):
    """Test suite for intermediate key grouping and shuffle partitioning."""

    def setUp(self):
        self.shuffle_mgr = ShuffleManager(num_reducers=2)

    def test_group_by_key(self):
        """Should group multiple occurrences of the same key into a value list."""
        # Scaffolding placeholder for Member 2
        # sample_pairs = [("error", 1), ("info", 1), ("error", 1)]
        # grouped = self.shuffle_mgr.group_by_key(sample_pairs)
        # self.assertEqual(grouped["error"], [1, 1])
        # self.assertEqual(grouped["info"], [1])
        pass

    def test_shuffle_and_partition_structure(self):
        """Partitions dictionary should contain keys for all reducer indices."""
        # Scaffolding placeholder for Member 2
        pass


if __name__ == "__main__":
    unittest.main()
