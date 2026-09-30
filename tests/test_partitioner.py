"""
tests/test_partitioner.py
=========================
Unit tests for Partitioner module (Member 2).

Covers:
- Strict key routing consistency (same key always routes to same partition)
- Valid partition index boundaries [0, num_reducers - 1]
- Deterministic behavior across multiple runs
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.partitioner import Partitioner


class TestPartitioner(unittest.TestCase):
    """Test suite for deterministic key-to-reducer partitioning."""

    def test_partition_consistency(self):
        """Identical keys must consistently hash to the exact same partition ID."""
        partitioner = Partitioner(num_reducers=3)
        p1 = partitioner.get_partition("error")
        p2 = partitioner.get_partition("error")
        p3 = partitioner.get_partition("database")
        self.assertEqual(p1, p2)
        # Verify result is repeatable
        self.assertEqual(partitioner.get_partition("error"), p1)

    def test_partition_boundary(self):
        """Partition IDs must fall strictly within range [0, num_reducers - 1]."""
        num_reducers = 4
        partitioner = Partitioner(num_reducers=num_reducers)
        test_keys = ["error", "warning", "info", "debug", "fatal", "trace", "critical"]

        for key in test_keys:
            pid = partitioner.get_partition(key)
            self.assertGreaterEqual(pid, 0)
            self.assertLess(pid, num_reducers)

    def test_invalid_reducer_count(self):
        """Initializing with less than 1 reducer should raise ValueError."""
        with self.assertRaises(ValueError):
            Partitioner(num_reducers=0)
        with self.assertRaises(ValueError):
            Partitioner(num_reducers=-1)


if __name__ == "__main__":
    unittest.main()
