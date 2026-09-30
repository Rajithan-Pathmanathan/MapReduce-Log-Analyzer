"""
tests/test_shuffle.py
=====================
Unit tests for ShuffleManager (Member 2).

Covers:
- Grouping flat intermediate pairs by unique key
- Same key coming from different Map workers ends up in one group
- Distribution of grouped keys into reducer-specific partitions
- Empty input
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.partitioner import Partitioner
from src.shuffle import ShuffleManager


class TestShuffleManager(unittest.TestCase):
    """Test suite for intermediate key grouping and shuffle partitioning."""

    def setUp(self):
        self.shuffle_mgr = ShuffleManager(num_reducers=2)

    def test_group_by_key(self):
        """Should group multiple occurrences of the same key into a value list."""
        grouped = self.shuffle_mgr.group_by_key([("error", 1), ("info", 1), ("error", 1)])
        self.assertEqual(grouped, {"error": [1, 1], "info": [1]})

    def test_same_key_from_different_map_workers(self):
        """Output of three mappers, concatenated, groups 'error' into one list."""
        mapper1 = [("error", 1), ("database", 1)]
        mapper2 = [("error", 1), ("info", 1)]
        mapper3 = [("error", 1), ("database", 1)]
        grouped = self.shuffle_mgr.group_by_key(mapper1 + mapper2 + mapper3)
        self.assertEqual(grouped["error"], [1, 1, 1])
        self.assertEqual(grouped["database"], [1, 1])

    def test_shuffle_and_partition_structure(self):
        """Partitions dictionary should contain keys for all reducer indices."""
        for n in (1, 2, 3, 5):
            partitions = ShuffleManager(n).shuffle_and_partition([("error", 1)])
            self.assertEqual(sorted(partitions), list(range(n)))

    def test_each_key_in_exactly_one_partition(self):
        pairs = [(k, 1) for k in ["error", "warning", "info", "database", "server", "login"] * 3]
        mgr = ShuffleManager(3)
        partitions = mgr.shuffle_and_partition(pairs)
        seen = [key for part in partitions.values() for key in part]
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(set(seen), {k for k, _ in pairs})
        for r_id, part in partitions.items():
            for key, values in part.items():
                self.assertEqual(Partitioner(3).get_partition(key), r_id)
                self.assertEqual(values, [1, 1, 1])

    def test_empty_input(self):
        self.assertEqual(self.shuffle_mgr.group_by_key([]), {})
        self.assertEqual(self.shuffle_mgr.shuffle_and_partition([]), {0: {}, 1: {}})


if __name__ == "__main__":
    unittest.main()
