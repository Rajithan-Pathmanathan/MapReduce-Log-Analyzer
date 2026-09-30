"""
src/partitioner.py
==================
Deterministic key partitioning module for the MapReduce pipeline.

Primary Ownership: Member 2 (Shuffle/Partition + Reduce Phase)

Responsibilities:
- Assign intermediate keys to specific reducer partitions.
- Ensure strict partition consistency: ALL occurrences of the exact same key
  MUST be routed to the exact same reducer partition ID.
- Provide a deterministic hashing mechanism (e.g., MD5 or SHA-256 hash modulo reducer_count)
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
            raise ValueError("Number of reducers must be at least 1.")
        self.num_reducers = num_reducers

    def get_partition(self, key: str) -> int:
        """
        Compute the partition index for a given intermediate key.

        :param key: Intermediate key string (e.g., 'error', 'database').
        :return: Integer partition ID in range [0, num_reducers - 1].
        """
        raise NotImplementedError("Member 2 to implement get_partition using deterministic hashing.")
