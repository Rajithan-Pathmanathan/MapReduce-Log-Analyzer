"""
tests/test_partitioner.py
=========================
Unit tests for Partitioner module (Member 2).

Covers:
- Strict key routing consistency (same key always routes to same partition)
- Valid partition index boundaries [0, num_reducers - 1]
- Deterministic behavior across separate processes with different hash seeds
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.partitioner import Partitioner

KEYS = ["error", "warning", "info", "database", "server", "login", "timeout", "db_pool"]


class TestPartitioner(unittest.TestCase):
    """Test suite for deterministic key-to-reducer partitioning."""

    def test_partition_consistency(self):
        """Identical keys must consistently hash to the exact same partition ID."""
        partitioner = Partitioner(num_reducers=3)
        for key in KEYS:
            self.assertEqual(partitioner.get_partition(key), partitioner.get_partition(key))

    def test_partition_boundary(self):
        """Partition IDs must fall strictly within range [0, num_reducers - 1]."""
        for n in (1, 2, 3, 7):
            partitioner = Partitioner(num_reducers=n)
            for key in KEYS:
                self.assertIn(partitioner.get_partition(key), range(n))

    def test_single_reducer_gets_everything(self):
        partitioner = Partitioner(num_reducers=1)
        self.assertEqual({partitioner.get_partition(k) for k in KEYS}, {0})

    def test_same_result_in_other_processes(self):
        """Routing must not depend on Python's per-process hash seed."""
        code = (
            "from src.partitioner import Partitioner;"
            f"print([Partitioner(3).get_partition(k) for k in {KEYS!r}])"
        )
        results = set()
        for seed in ("1", "2", "3"):
            env = dict(os.environ, PYTHONHASHSEED=seed)
            out = subprocess.run(
                [sys.executable, "-c", code], cwd=PROJECT_ROOT, env=env,
                capture_output=True, text=True, check=True,
            ).stdout.strip()
            results.add(out)
        expected = str([Partitioner(3).get_partition(k) for k in KEYS])
        self.assertEqual(results, {expected})

    def test_invalid_reducer_count(self):
        """Initializing with less than 1 reducer should raise ValueError."""
        with self.assertRaises(ValueError):
            Partitioner(num_reducers=0)


if __name__ == "__main__":
    unittest.main()
