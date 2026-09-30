# Development Workflow & Member Responsibilities

**Module:** INTE 22253 – Distributed Systems and Cloud Computing  
**Project:** MapReduce Log Analysis System  
**Team Structure:** Three Independent Student Workstreams

---

## 1. End-to-End Pipeline Workflow

```
[Input Directory]
       │
       ▼ (File Discovery & Validation)
[InputManager]
       │
       ▼ (Balanced Splits)
[Coordinator] ─── spawns ───► [Map Workers 1..M]
                                       │
                                       ▼ (Emits: List[Tuple[str, int]])
                              [Intermediate Pairs]
                                       │
                                       ▼ (Grouping & Deterministic Hash Partitioning)
                              [ShuffleManager]
                                       │
                                       ▼ (Dict[partition_id, Dict[key, List[int]]])
[Coordinator] ─── spawns ───► [Reduce Workers 1..R]
                                       │
                                       ▼ (Emits: List[Tuple[str, int]])
                              [Reduced Partitions]
                                       │
                                       ▼ (Consolidation, Sorting, Formatting)
                              [OutputManager]
                                       │
                                       ▼
                       [output/result.txt] + Terminal UI
```

---

## 2. Team Division of Responsibilities

### Member 1: Coordinator + Map Phase
- **Primary Source Modules:** `src/input_manager.py`, `src/mapper.py`, `src/coordinator.py`
- **Primary Test Modules:** `tests/test_input_manager.py`, `tests/test_mapper.py`
- **Responsibilities:**
  - Input file discovery and format validation.
  - Calculation of dataset file size.
  - Workload partitioning into balanced input splits.
  - Process-based Map worker invocation using Python `multiprocessing`.
  - Log line tokenization, cleaning, and intermediate `(key, 1)` pair emission.
  - Map phase timing measurements.
  - Unit tests for input management and map worker tasks.

### Member 2: Shuffle/Partition + Reduce Phase
- **Primary Source Modules:** `src/partitioner.py`, `src/shuffle.py`, `src/reducer.py`
- **Primary Test Modules:** `tests/test_partitioner.py`, `tests/test_shuffle.py`, `tests/test_reducer.py`
- **Responsibilities:**
  - Intermediate key-value grouping (`key -> [1, 1, 1, ...]`).
  - Deterministic hash-based partitioner implementation (`hash(key) % R`).
  - Strict key-to-reducer routing guarantee (same key always sent to same partition).
  - Reduce worker process function and aggregation logic.
  - Handling of uneven key distributions and edge cases.
  - Unit tests for partitioning, shuffling, and reduction.

### Member 3: Integration + Testing + Documentation
- **Primary Source Modules:** `src/output_manager.py`, `src/main.py`
- **Primary Test & Doc Modules:** `tests/test_integration.py`, `docs/*`, `README.md`
- **Responsibilities:**
  - Integration of Member 1 and Member 2 modules into an end-to-end executable pipeline.
  - Command-line argument parsing and execution entry point (`main.py`).
  - Formatting results, sorting Top-N frequencies, and writing output files.
  - Execution summary reporting designed for university evaluation (Figure 7 terminal screenshot).
  - Comprehensive integration testing verifying overall correctness.
  - Execution of performance experiments (recording actual wall-clock metrics across 1, 2, and 4 workers).
  - Final documentation, report readiness, and codebase packaging.

---

## 3. Critical Shared Interfaces

To allow independent development without merge friction or integration breaks, members must strictly adhere to these interfaces:

### Interface A: Map Worker Output -> Shuffle Input
- **Producer:** Member 1 (`src/mapper.py`)
- **Consumer:** Member 2 (`src/shuffle.py`)
- **Data Specification:**
  ```python
  # Flat list of 2-tuples containing token key and integer occurrence
  intermediate_pairs: List[Tuple[str, int]]
  # Example: [("error", 1), ("database", 1), ("error", 1)]
  ```

### Interface B: Shuffle/Partition Output -> Reduce Worker Input
- **Producer:** Member 2 (`src/shuffle.py`, `src/partitioner.py`)
- **Consumer:** Member 2 (`src/reducer.py`) / Member 1 Coordinator
- **Data Specification:**
  ```python
  # Dictionary mapping integer partition_id [0 .. num_reducers-1]
  # to a sub-dictionary mapping keys to lists of values
  partitions: Dict[int, Dict[str, List[int]]]
  # Example: {
  #   0: {"error": [1, 1], "warning": [1]},
  #   1: {"database": [1], "login": [1, 1]}
  # }
  ```

### Interface C: Reduce Worker Output -> Output Manager Input
- **Producer:** Member 2 (`src/reducer.py`)
- **Consumer:** Member 3 (`src/output_manager.py`)
- **Data Specification:**
  ```python
  # List of reduced lists from each worker, containing (key, aggregated_count)
  reducer_results: List[List[Tuple[str, int]]]
  # Example: [
  #   [("error", 2), ("warning", 1)],
  #   [("database", 1), ("login", 2)]
  # ]
  ```
