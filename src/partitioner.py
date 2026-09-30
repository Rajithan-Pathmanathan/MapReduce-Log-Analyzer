"""
src/partitioner.py
==================
Deterministic key partitioning module for the MapReduce pipeline.

Primary Ownership: Member 2 (Shuffle/Partition + Reduce Phase)

Responsibilities:
- Assign intermediate keys to specific reducer partitions.
- Ensure strict partition consistency: ALL occurrences of the exact same key
  MUST be routed to the exact same reducer partition ID.
- Provide a deterministic hashing mechanism (MD5 hash modulo reducer_count)
  to ensure reproducible execution independent of Python's randomized hash seed.

Conceptual Formula:
    partition_id = int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) % num_reducers
"""

import hashlib


class Partitioner:
    """Assigns intermediate keys to designated reducer partitions deterministically."""

    def __init__(self, num_reducers: int):
        """
        Initialize the partitioner with the total number of reduce workers.

        :param num_reducers: Number of reduce workers/partitions (must be >= 1).
        """
        if num_reducers < 1:
            raise ValueError(f"Number of reducers must be >= 1, received: {num_reducers}")
        self.num_reducers = num_reducers

    def get_partition(self, key: str) -> int:
        """
        Compute the partition index for a given intermediate key deterministically.

        :param key: Intermediate key string (e.g., 'error', 'database').
        :return: Integer partition ID in range [0, num_reducers - 1].
        """
        # MD5 digest provides stable, process-independent deterministic integer hashing
        digest = hashlib.md5(key.encode("utf-8")).hexdigest()
        return int(digest, 16) % self.num_reducers
