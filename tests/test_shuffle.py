"""
tests/test_shuffle.py
=====================
Unit tests for ShuffleManager (Member 2).

Covers:
- Grouping flat intermediate pairs by unique key
- Distribution of grouped keys into reducer-specific partitions
- Strict partition membership for identical keys
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
        self.num_reducers = 2
        self.shuffle_mgr = ShuffleManager(num_reducers=self.num_reducers)

    def test_group_by_key(self):
        """Should group multiple occurrences of the same key into a value list."""
        sample_pairs = [("error", 1), ("info", 1), ("error", 1), ("warning", 1)]
        grouped = self.shuffle_mgr.group_by_key(sample_pairs)

        self.assertEqual(grouped["error"], [1, 1])
        self.assertEqual(grouped["info"], [1])
        self.assertEqual(grouped["warning"], [1])

    def test_shuffle_and_partition_structure(self):
        """Partitions dictionary should contain keys for all reducer indices."""
        sample_pairs = [("error", 1), ("info", 1), ("error", 1), ("login", 1)]
        partitions = self.shuffle_mgr.shuffle_and_partition(sample_pairs)

        self.assertEqual(len(partitions), self.num_reducers)
        for r_id in range(self.num_reducers):
            self.assertIn(r_id, partitions)
            self.assertIsInstance(partitions[r_id], dict)

        # Ensure all intermediate pairs are accounted for
        total_occurrences = sum(
            sum(len(vals) for vals in part_dict.values())
            for part_dict in partitions.values()
        )
        self.assertEqual(total_occurrences, 4)

    def test_shuffle_empty_input(self):
        """Empty intermediate pairs should result in empty partition buckets."""
        partitions = self.shuffle_mgr.shuffle_and_partition([])
        self.assertEqual(len(partitions), self.num_reducers)
        for r_id in range(self.num_reducers):
            self.assertEqual(partitions[r_id], {})


if __name__ == "__main__":
    unittest.main()
