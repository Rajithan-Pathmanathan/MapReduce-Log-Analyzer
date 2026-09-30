"""
tests/test_coordinator.py
=========================
Tests for the Member 1 part of the Coordinator: input measurement,
byte-range splitting and the parallel Map stage.

Covers:
- Normal input
- Empty input file
- Multiple files
- Multiple Map workers (different PIDs, same result as 1 worker)
- Repeated terms
- Missing / empty input directory
"""

import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.coordinator import Coordinator


class TestCoordinatorMapStage(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, text):
        (self.tmp / name).write_bytes(text.encode("utf-8"))

    def _run(self, **overrides):
        cfg = Config(input_dir=self.tmp, output_dir=self.tmp / "out", verbose=False, **overrides)
        coord = Coordinator(cfg)
        return coord, coord.run_map_stage()

    def test_normal_input(self):
        self._write("a.log", "ERROR database connection failed\n")
        _, pairs = self._run(map_workers=1)
        self.assertEqual(
            pairs,
            [("error", 1), ("database", 1), ("connection", 1), ("failed", 1)],
        )

    def test_empty_file_with_other_files(self):
        self._write("empty.log", "")
        self._write("a.log", "error error info\n")
        coord, pairs = self._run()
        self.assertEqual(Counter(k for k, _ in pairs), {"error": 2, "info": 1})
        self.assertEqual(coord.metrics["input_files_count"], 2)

    def test_multiple_files_and_repeated_terms(self):
        # Test E dataset from the spec
        self._write("f1.log", "error error info\n")
        self._write("f2.log", "error warning info\n")
        coord, pairs = self._run(map_workers=2)
        self.assertEqual(Counter(k for k, _ in pairs), {"error": 3, "info": 2, "warning": 1})
        self.assertTrue(all(v == 1 for _, v in pairs))
        self.assertEqual(coord.metrics["intermediate_pairs"], 6)

    def test_metrics_are_measured(self):
        self._write("a.log", "error one\nwarning two\n")
        self._write("b.txt", "info three")
        coord, _ = self._run()
        m = coord.metrics
        self.assertEqual(m["input_files_count"], 2)
        self.assertEqual(m["total_input_bytes"], 22 + 10)
        self.assertEqual(m["total_input_lines"], 3)
        self.assertGreater(m["map_time_seconds"], 0)

    def test_multiple_workers_match_single_worker(self):
        # Small split size forces many splits; lines crossing split
        # boundaries must be counted exactly once.
        lines = [f"line {i} error server{i % 7} login\n" for i in range(500)]
        self._write("big.log", "".join(lines))
        coord1, pairs1 = self._run(map_workers=1, split_size_bytes=64)
        coord4, pairs4 = self._run(map_workers=4, split_size_bytes=64)
        self.assertGreater(coord4.metrics["input_splits"], 4)
        self.assertEqual(pairs1, pairs4)
        self.assertEqual(Counter(k for k, _ in pairs4)["error"], 500)
        self.assertEqual(coord1.metrics["total_input_lines"], 500)

    def test_only_empty_files_gives_no_pairs(self):
        self._write("empty.log", "")
        coord, pairs = self._run()
        self.assertEqual(pairs, [])
        self.assertEqual(coord.metrics["input_splits"], 0)

    def test_empty_directory_raises(self):
        with self.assertRaises(ValueError):
            self._run()

    def test_missing_directory_raises(self):
        cfg = Config(input_dir=self.tmp / "nope", verbose=False)
        with self.assertRaises(FileNotFoundError):
            Coordinator(cfg).run_map_stage()


if __name__ == "__main__":
    unittest.main()
