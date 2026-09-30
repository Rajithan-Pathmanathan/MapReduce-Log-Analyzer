"""
src/main.py
===========
Main entry point for the MapReduce Log Analysis System.

Primary Ownership: Member 3 (Integration + Testing + Documentation)

Responsibilities:
- Parse command-line arguments (optional overrides for worker counts and paths).
- Initialize system configuration.
- Instantiate and trigger the MapReduce Coordinator.
- Present clean execution outputs and execution time statistics.

Usage:
    python src/main.py
    python src/main.py --map-workers 4 --reduce-workers 2 --input sample_data/small
"""

import argparse
import multiprocessing
import sys
from pathlib import Path

# Ensure project root is in sys.path for direct script execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import Config, DEFAULT_CONFIG
from src.coordinator import Coordinator


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options for running the MapReduce pipeline."""
    parser = argparse.ArgumentParser(
        description="Local MapReduce Log Analysis System (Multiprocessing Simulation)"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_CONFIG.input_dir,
        help="Path to directory containing input log files (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_CONFIG.output_dir,
        help="Path to output directory (default: %(default)s)",
    )
    parser.add_argument(
        "-m",
        "--map-workers",
        type=int,
        default=DEFAULT_CONFIG.map_workers,
        help="Number of parallel Map workers (default: %(default)s)",
    )
    parser.add_argument(
        "-r",
        "--reduce-workers",
        type=int,
        default=DEFAULT_CONFIG.reduce_workers,
        help="Number of parallel Reduce workers (default: %(default)s)",
    )
    parser.add_argument(
        "-t",
        "--top-n",
        type=int,
        default=DEFAULT_CONFIG.top_n_results,
        help="Number of top frequent keys to display (default: %(default)s)",
    )
    args = parser.parse_args()
    for name in ("map_workers", "reduce_workers", "top_n"):
        if getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must be >= 1")
    return args


def main() -> None:
    """Application entry point."""
    args = parse_arguments()

    config = Config(
        input_dir=args.input,
        output_dir=args.output,
        map_workers=args.map_workers,
        reduce_workers=args.reduce_workers,
        top_n_results=args.top_n,
    )

    print("==================================================")
    print("      MAPREDUCE LOG ANALYZER (SIMULATION)         ")
    print("==================================================")
    print(f"Input Directory  : {config.input_dir}")
    print(f"Output Directory : {config.output_dir}")
    print(f"Map Workers      : {config.map_workers}")
    print(f"Reduce Workers   : {config.reduce_workers}")
    print("==================================================")

    try:
        coordinator = Coordinator(config)
        coordinator.execute_job()
    except Exception as exc:
        print(f"[ERROR] Execution failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Required for Windows multiprocessing support to prevent recursive process spawning
    multiprocessing.freeze_support()
    main()
