"""
src/reducer.py
==============
Reduce worker and aggregation module.

Primary Ownership: Member 2 (Shuffle/Partition + Reduce Phase)

Responsibilities:
- Process an assigned partition dictionary: {key: [v1, v2, ...]}.
- Aggregate values for each key (e.g., summation of occurrences).
- Return reduced (key, aggregated_value) pairs.
- Execute in parallel worker processes simulated via Python multiprocessing.

Conceptual Transformation:
    Partition Input:
        {"error": [1, 1, 1], "warning": [1]}
    Reducer Output:
        {"error": 3, "warning": 1}
"""

from typing import Dict, List, Tuple


def reduce_values(key: str, values: List[int]) -> int:
    """
    Aggregate the values associated with a single key.

    :param key: The key being reduced (e.g., 'error').
    :param values: List of integer occurrences (e.g., [1, 1, 1]).
    :return: Aggregated total count.
    """
    raise NotImplementedError("Member 2 to implement reduce_values.")


def reduce_worker(
    partition_data: Dict[str, List[int]], worker_id: int
) -> List[Tuple[str, int]]:
    """
    Reduce worker process function executed in parallel.
    Aggregates all key-value lists assigned to this reducer partition.

    :param partition_data: Dict mapping keys to their lists of occurrences.
    :param worker_id: Numeric identifier for the reduce worker.
    :return: List of finalized (key, count) tuples for this partition.
    """
    raise NotImplementedError("Member 2 to implement reduce_worker.")
