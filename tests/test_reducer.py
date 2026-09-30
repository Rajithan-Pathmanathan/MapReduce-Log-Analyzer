"""
tests/test_reducer.py
=====================
Unit tests for Reducer module (Member 2).

Covers:
- Aggregating list of values for individual keys
- Processing full partition dictionaries in reduce workers
- Correctness of count summation
- Handling empty partitions
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.reducer import reduce_values, reduce_worker


class TestReducer(unittest.TestCase):
    """Test suite for reduce phase aggregation."""

    def test_reduce_values_sum(self):
        """Should sum all occurrences for a specific key."""
        result = reduce_values("error", [1, 1, 1, 1])
        self.assertEqual(result, 4)

    def test_reduce_values_single(self):
        """Single occurrence should yield 1."""
        result = reduce_values("warning", [1])
        self.assertEqual(result, 1)

    def test_reduce_worker_output(self):
        """Should aggregate all keys present within the partition."""
        partition_data = {"error": [1, 1, 1], "info": [1, 1], "database": [1]}
        output = reduce_worker(partition_data, worker_id=0)

        result_dict = dict(output)
        self.assertEqual(result_dict["error"], 3)
        self.assertEqual(result_dict["info"], 2)
        self.assertEqual(result_dict["database"], 1)

    def test_reduce_worker_empty_partition(self):
        """Empty partition should return an empty list."""
        output = reduce_worker({}, worker_id=1)
        self.assertEqual(output, [])


if __name__ == "__main__":
    unittest.main()
