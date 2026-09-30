"""
tests/test_reducer.py
=====================
Unit tests for Reducer module (Member 2).

Covers:
- Aggregating list of values for individual keys
- Processing full partition dictionaries in reduce workers
- Multiple reducers run as parallel processes through the Coordinator
- Known small input with manually verified results
- Empty partitions
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.coordinator import Coordinator
from src.reducer import reduce_values, reduce_worker
from src.shuffle import ShuffleManager


class TestReducer(unittest.TestCase):
    """Test suite for reduce phase aggregation."""

    def test_reduce_values_sum(self):
        """Should sum all occurrences for a specific key."""
        self.assertEqual(reduce_values("error", [1, 1, 1, 1]), 4)
        self.assertEqual(reduce_values("info", [1]), 1)

    def test_reduce_worker_output(self):
        """Should aggregate all keys present within the partition."""
        output = reduce_worker({"error": [1, 1], "info": [1]}, worker_id=0)
        self.assertEqual(sorted(output), [("error", 2), ("info", 1)])

    def test_empty_partition(self):
        self.assertEqual(reduce_worker({}, worker_id=1), [])

    def test_known_small_input(self):
        """Spec example: error, error, info -> error = 2, info = 1."""
        pairs = [("error", 1), ("error", 1), ("info", 1)]
        partitions = ShuffleManager(2).shuffle_and_partition(pairs)
        results = [p for r_id, part in partitions.items() for p in reduce_worker(part, r_id)]
        self.assertEqual(dict(results), {"error": 2, "info": 1})

    def test_multiple_reducers_in_parallel(self):
        """Coordinator runs one process per reducer; totals match a single reducer."""
        words = ["error"] * 25 + ["database"] * 17 + ["warning"] * 12 + ["info"] * 9 + ["login"] * 3
        pairs = [(w, 1) for w in words]
        totals = {}
        for n in (1, 3):
            coord = Coordinator(Config(reduce_workers=n, verbose=False))
            outputs = coord.run_reduce_phase(coord.shuffle_manager.shuffle_and_partition(pairs))
            self.assertEqual(len(outputs), n)
            totals[n] = dict(p for out in outputs for p in out)
        self.assertEqual(totals[1], totals[3])
        self.assertEqual(totals[3], {"error": 25, "database": 17, "warning": 12, "info": 9, "login": 3})


if __name__ == "__main__":
    unittest.main()
