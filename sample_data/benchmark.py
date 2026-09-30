"""
sample_data/benchmark.py
========================
Runs the real pipeline with different worker counts and prints a Markdown
table of measured timings (median of REPEATS runs per configuration).

Usage:
    python sample_data/benchmark.py
    python sample_data/benchmark.py --input sample_data/small --repeats 5
"""

import argparse
import multiprocessing
import platform
import statistics
import sys
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config
from src.coordinator import Coordinator

CONFIGS = [(1, 1), (2, 1), (2, 2), (4, 2), (8, 4)]  # (map workers, reduce workers)
PHASES = ["map_time_seconds", "shuffle_time_seconds", "reduce_time_seconds",
          "total_execution_time_seconds"]


def run_once(input_dir: Path, map_workers: int, reduce_workers: int) -> dict:
    with tempfile.TemporaryDirectory() as out_dir:
        config = Config(input_dir=input_dir, output_dir=Path(out_dir),
                        map_workers=map_workers, reduce_workers=reduce_workers,
                        verbose=False)
        with redirect_stdout(StringIO()):  # hide the per-run summary
            return Coordinator(config).execute_job()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[3])
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "sample_data" / "medium")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    print(f"Python {platform.python_version()} on {platform.platform()}, "
          f"{multiprocessing.cpu_count()} logical CPUs")
    rows, first = [], None
    for m, r in CONFIGS:
        runs = [run_once(args.input, m, r) for _ in range(args.repeats)]
        first = first or runs[0]
        results = {tuple(run["results"]) for run in runs}
        assert len(results) == 1, "results differ between runs"
        med = {p: statistics.median(run["metrics"][p] for run in runs) for p in PHASES}
        rows.append((m, r, runs[0], med))

    # Every configuration must produce identical counts
    assert len({tuple(row[2]["results"]) for row in rows}) == 1, "results differ between configs"

    fm = first["metrics"]
    print(f"Input: {args.input} | files {fm['input_files_count']} | "
          f"{fm['total_input_bytes']:,} bytes | {fm['total_input_lines']:,} lines | "
          f"{fm['input_splits']} splits | {fm['intermediate_pairs']:,} pairs | "
          f"{len(first['results'])} unique keys | median of {args.repeats} runs\n")
    print("| Map workers | Reduce workers | Map (s) | Shuffle (s) | Reduce (s) | Total (s) |")
    print("| :---: | :---: | :---: | :---: | :---: | :---: |")
    for m, r, _, med in rows:
        print(f"| {m} | {r} | {med['map_time_seconds']:.4f} | {med['shuffle_time_seconds']:.4f} | "
              f"{med['reduce_time_seconds']:.4f} | **{med['total_execution_time_seconds']:.4f}** |")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
