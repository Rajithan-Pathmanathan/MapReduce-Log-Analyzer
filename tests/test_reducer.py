"""
tests/test_reducer.py
=====================
Unit tests for Reducer module (Member 2).

Covers:
- Aggregating list of values for individual keys
- Processing full partition dictionaries in reduce workers
- Correctness of count summation
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
        # Scaffolding placeholder for Member 2
        # result = reduce_values("error", [1, 1, 1, 1])
        # self.assertEqual(result, 4)
        pass

    def test_reduce_worker_output(self):
        """Should aggregate all keys present within the partition."""
        # Scaffolding placeholder for Member 2
        # partition_data = {"error": [1, 1], "info": [1]}
        # output = reduce_worker(partition_data, worker_id=0)
        # self.assertIn(("error", 2), output)
        # self.assertIn(("info", 1), output)
        pass


if __name__ == "__main__":
    unittest.main()
