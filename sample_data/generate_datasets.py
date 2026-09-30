"""
sample_data/generate_datasets.py
================================
Utility script to generate realistic server log datasets for testing and benchmarking.
Uses a deterministic random seed to ensure reproducible dataset generation.
"""

import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
SMALL_DIR = DATA_DIR / "small"
MEDIUM_DIR = DATA_DIR / "medium"

LOG_LEVELS = ["INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"]
SERVICES = ["auth-service", "payment-gateway", "inventory-api", "db-cluster", "web-frontend"]
MESSAGES = [
    "User authentication failed for account admin",
    "Database connection pool exhausted waiting for available connection",
    "Transaction timeout after 5000ms on payment gateway",
    "High memory usage detected on server cluster node",
    "Cache miss for product inventory key",
    "SSL handshake failed from remote client IP",
    "HTTP 500 internal server error during checkout process",
    "Periodic database backup completed successfully",
    "User logged in from remote session",
    "Disk space warning volume reaching 85 percent threshold",
    "Circuit breaker opened due to repeated network timeouts",
    "Worker heartbeat received from node",
    "Database query executed in 142ms",
    "Rate limit exceeded for client IP request",
    "Failed to acquire distributed lock for session",
]

IP_POOL = [f"192.168.1.{i}" for i in range(10, 50)]


def generate_log_line(random_gen: random.Random, line_num: int) -> str:
    """Generate a single formatted server log record."""
    timestamp = f"2026-09-30T14:{line_num % 60:02d}:{(line_num * 7) % 60:02d}.000Z"
    level = random_gen.choices(LOG_LEVELS, weights=[50, 20, 15, 5, 10])[0]
    service = random_gen.choice(SERVICES)
    msg = random_gen.choice(MESSAGES)
    ip = random_gen.choice(IP_POOL)
    return f"[{timestamp}] [{level}] [{service}] [{ip}] - {msg}"


def generate_dataset(target_dir: Path, file_count: int, lines_per_file: int, seed: int = 42) -> None:
    """Generate a set of log files deterministically."""
    target_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    for i in range(1, file_count + 1):
        file_path = target_dir / f"server_{i}.log"
        with open(file_path, "w", encoding="utf-8") as f:
            for line_idx in range(lines_per_file):
                f.write(generate_log_line(rng, line_idx) + "\n")
        print(f"Generated {file_path.name} ({lines_per_file} lines)")


def main():
    print("Generating Small Dataset (< 1 MB)...")
    generate_dataset(SMALL_DIR, file_count=4, lines_per_file=250, seed=100)
    # Add an empty log file to small dataset to test Test B condition
    (SMALL_DIR / "empty.log").write_text("", encoding="utf-8")
    print("Generated empty.log (0 bytes)")

    print("\nGenerating Medium Dataset (Multi-MB benchmark)...")
    generate_dataset(MEDIUM_DIR, file_count=5, lines_per_file=6000, seed=200)

    print("\nDone generating datasets.")


if __name__ == "__main__":
    main()
