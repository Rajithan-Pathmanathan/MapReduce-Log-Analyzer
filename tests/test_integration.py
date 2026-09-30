"""
tests/test_integration.py
=========================
End-to-end integration tests for MapReduce Log Analysis System (Member 3).

Validates the full pipeline:
Input Files -> Coordinator -> Map Workers -> Shuffle/Partition -> Reduce Workers -> Final Output

Test Suite Matrix:
- Test A: Normal workload (several log files with repeated terms)
- Test B: Empty file handling (clean execution without errors)
- Test C: Multiple files aggregation correctness
- Test D: Multiple workers configuration execution
- Test E: Known expected result validation
    File 1: "error error info"
    File 2: "error warning info"
    Expected: error = 3, info = 2, warning = 1
"""

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.coordinator import Coordinator


class TestMapReduceIntegration(unittest.TestCase):
    """End-to-end integration testing suite for MapReduce pipeline."""

    def setUp(self):
        """Create isolated temporary input and output directories."""
        self.temp_in_obj = tempfile.TemporaryDirectory()
        self.temp_out_obj = tempfile.TemporaryDirectory()
        self.input_dir = Path(self.temp_in_obj.name)
        self.output_dir = Path(self.temp_out_obj.name)

    def tearDown(self):
        """Clean up temporary test directories."""
        self.temp_in_obj.cleanup()
        self.temp_out_obj.cleanup()

    def test_a_normal_workload(self):
        """Test A: Normal workload with several files and repeated terms."""
        f1 = self.input_dir / "app1.log"
        f2 = self.input_dir / "app2.log"
        f1.write_text("INFO server started\nERROR disk full\nINFO client connected\n", encoding="utf-8")
        f2.write_text("ERROR disk full\nWARNING high memory\nINFO server started\n", encoding="utf-8")

        config = Config(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            map_workers=2,
            reduce_workers=2,
        )
        coordinator = Coordinator(config)
        summary = coordinator.execute_job()

        results_dict = dict(summary["results"])
        self.assertEqual(results_dict["server"], 2)
        self.assertEqual(results_dict["started"], 2)
        self.assertEqual(results_dict["disk"], 2)
        self.assertEqual(results_dict["full"], 2)
        self.assertEqual(results_dict["error"], 2)
        self.assertEqual(results_dict["info"], 3)
        self.assertEqual(results_dict["warning"], 1)

    def test_b_empty_file(self):
        """Test B: Handling of empty input files alongside valid files."""
        f1 = self.input_dir / "normal.log"
        f2 = self.input_dir / "empty.log"
        f1.write_text("database timeout failure\n", encoding="utf-8")
        f2.write_text("", encoding="utf-8")  # Completely empty file

        config = Config(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            map_workers=2,
            reduce_workers=1,
        )
        coordinator = Coordinator(config)
        summary = coordinator.execute_job()

        results_dict = dict(summary["results"])
        self.assertEqual(results_dict["database"], 1)
        self.assertEqual(results_dict["timeout"], 1)
        self.assertEqual(results_dict["failure"], 1)
        self.assertEqual(summary["metrics"]["input_files_count"], 2)

    def test_c_multiple_files(self):
        """Test C: Multi-file aggregation across 4 distinct log files."""
        terms = ["cluster", "node", "heartbeat"]
        for i in range(4):
            f = self.input_dir / f"node_{i}.log"
            # Each file writes: cluster node heartbeat
            f.write_text(f"{terms[0]} {terms[1]} {terms[2]}\n", encoding="utf-8")

        config = Config(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            map_workers=4,
            reduce_workers=2,
        )
        coordinator = Coordinator(config)
        summary = coordinator.execute_job()

        results_dict = dict(summary["results"])
        self.assertEqual(results_dict["cluster"], 4)
        self.assertEqual(results_dict["node"], 4)
        self.assertEqual(results_dict["heartbeat"], 4)

    def test_d_multiple_workers(self):
        """Test D: Multiple worker processes execute and complete cleanly."""
        for i in range(6):
            f = self.input_dir / f"service_{i}.log"
            f.write_text(f"worker test log entry {i}\n", encoding="utf-8")

        # 4 Map workers, 3 Reduce workers
        config = Config(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            map_workers=4,
            reduce_workers=3,
        )
        coordinator = Coordinator(config)
        summary = coordinator.execute_job()

        self.assertGreater(summary["metrics"]["total_execution_time_seconds"], 0.0)
        self.assertEqual(summary["metrics"]["map_workers"], 4)
        self.assertEqual(summary["metrics"]["reduce_workers"], 3)
        self.assertTrue(config.output_file_path.exists())

    def test_e_known_expected_result(self):
        """
        Test E: Exact academic validation test case from assignment prompt.
        File 1: error error info
        File 2: error warning info
        Expected: error = 3, info = 2, warning = 1
        """
        f1 = self.input_dir / "file1.log"
        f2 = self.input_dir / "file2.log"
        f1.write_text("error error info\n", encoding="utf-8")
        f2.write_text("error warning info\n", encoding="utf-8")

        config = Config(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            map_workers=2,
            reduce_workers=2,
        )
        coordinator = Coordinator(config)
        summary = coordinator.execute_job()

        results_dict = dict(summary["results"])
        self.assertEqual(results_dict.get("error"), 3)
        self.assertEqual(results_dict.get("info"), 2)
        self.assertEqual(results_dict.get("warning"), 1)


if __name__ == "__main__":
    unittest.main()
