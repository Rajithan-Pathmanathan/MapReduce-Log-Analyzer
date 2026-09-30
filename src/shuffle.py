"""
src/shuffle.py
==============
Intermediate data aggregation, grouping, and shuffle module.

Primary Ownership: Member 2 (Shuffle/Partition + Reduce Phase)

Responsibilities:
- Collect intermediate (key, value) pairs produced across all Map workers.
- Group values associated with identical keys together: key -> [v1, v2, ...].
- Apply the Partitioner to route grouped keys into distinct reducer buckets/partitions.
- Structure partition payloads ready for distribution to parallel Reduce workers.

Conceptual Transformation:
    Input:
        [("error", 1), ("info", 1), ("error", 1), ("warning", 1)]
    Grouped Intermediate:
        {"error": [1, 1], "info": [1], "warning": [1]}
    Partitioned for 2 Reducers:
        Partition 0: {"error": [1, 1], "warning": [1]}
        Partition 1: {"info": [1]}
"""

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple
from src.partitioner import Partitioner


class ShuffleManager:
    """Orchestrates grouping intermediate pairs and routing them into reducer partitions."""

    def __init__(self, num_reducers: int):
        """
        Initialize the ShuffleManager.

        :param num_reducers: Total number of reduce workers.
        """
        self.num_reducers = num_reducers
        self.partitioner = Partitioner(num_reducers)

    def group_by_key(
        self, intermediate_pairs: Iterable[Tuple[str, int]]
    ) -> Dict[str, List[int]]:
        """
        Group intermediate (key, value) pairs by their unique key.

        :param intermediate_pairs: Flat iterable of (key, value) tuples from Map workers.
        :return: Dictionary mapping each unique key to its list of values.
        """
        grouped: Dict[str, List[int]] = defaultdict(list)
        for key, value in intermediate_pairs:
            grouped[key].append(value)
        return dict(grouped)

    def shuffle_and_partition(
        self, intermediate_pairs: Iterable[Tuple[str, int]]
    ) -> Dict[int, Dict[str, List[int]]]:
        """
        Group intermediate pairs and distribute grouped keys into partition dictionaries
        indexed by reducer ID [0 .. num_reducers-1].

        :param intermediate_pairs: Flat iterable of (key, value) tuples from Map workers.
        :return: Dict mapping reducer_id to its assigned sub-dictionary of {key: [values]}.
        """
        # Initialize partition dictionaries for each reducer
        partitions: Dict[int, Dict[str, List[int]]] = {
            r_id: {} for r_id in range(self.num_reducers)
        }

        # Step 1: Group occurrences by key
        grouped_data = self.group_by_key(intermediate_pairs)

        # Step 2: Route each unique key to its deterministic partition
        for key, values in grouped_data.items():
            partition_id = self.partitioner.get_partition(key)
            partitions[partition_id][key] = values

        return partitions
