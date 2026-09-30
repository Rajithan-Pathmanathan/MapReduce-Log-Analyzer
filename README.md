# Local MapReduce Log Analysis System

**Course:** INTE 22253 – Distributed Systems and Cloud Computing  
**Institution:** University of Kelaniya, Faculty of Science, Department of Industrial Management  
**Assignment:** Assignment 01 – Part C – Option 2 (MapReduce Log Analysis System)  
**Team:** Pavithira Rajkumar (Member 1), Dayaleeswaran (Member 2), Rajithan Pathmanathan (Member 3)  

---

## 1. Project Purpose

Modern server and cloud infrastructure continuously generates large volumes of operational log files. Ingestion and aggregation of these logs sequentially on a single thread becomes a performance bottleneck as dataset sizes grow.

This project implements a **local, multi-process MapReduce log analysis pipeline** in Python. The system simulates distributed Map and Reduce workers on a multi-core machine using Python's standard `multiprocessing` library. The primary goals are:
- Demonstrate core MapReduce programming abstractions: input splitting, parallel mapping, intermediate key-value generation, deterministic shuffle/partitioning, parallel reduction, and final aggregation.
- Measure actual execution times and scaling behavior across varying worker configurations (1, 2, and 4 workers).
- Analyze the operational differences and trade-offs between a local multi-process simulation and a true cloud-native distributed deployment (e.g., Apache Hadoop, AWS EMR).

---

## 2. MapReduce Architecture

The execution pipeline adheres strictly to the canonical MapReduce data flow:

```
                    INPUT LOG FILES
                         │
                         ▼
                    COORDINATOR
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   MAP WORKER 1     MAP WORKER 2     MAP WORKER N
        │                │                │
        └────────────────┼────────────────┘
                         │ (Intermediate Key-Value Pairs)
                         ▼
                SHUFFLE / PARTITION
                         │ (Deterministic MD5 Routing)
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  REDUCE WORKER 1  REDUCE WORKER 2  REDUCE WORKER N
        │                │                │
        └────────────────┼────────────────┘
                         │ (Aggregated Partitions)
                         ▼
                    FINAL OUTPUT
```

### Stages of Execution:
1. **Input Splitting (`InputManager`):** Scans the input directory, validates file accessibility, measures file count, bytes and lines, and cuts every file into byte-range splits (default 256 KiB). A Map worker reads only its own range; each line belongs to the split containing its first byte.
2. **Parallel Map Phase (`mapper.py`):** Independent worker processes tokenize log records, filter noise, and emit intermediate key-value pairs `(token, 1)`.
3. **Shuffle & Partition Phase (`shuffle.py`, `partitioner.py`):** Aggregates intermediate pairs by unique key (`key -> [1, 1, ...]`) and applies deterministic hashing (`int(MD5(key), 16) % num_reducers`) to ensure identical keys always route to the same reducer partition.
4. **Parallel Reduce Phase (`reducer.py`):** Reducer worker processes sum the occurrences for all keys in their assigned partition bucket.
5. **Output Generation (`output_manager.py`):** Consolidates reduced partitions, sorts terms in descending frequency, prints a formatted execution summary to the console, and writes the persistent report to `output/result.txt`.

---

## 3. Project Structure

```text
MapReduce-Log-Analyzer/
│
├── README.md                          # Comprehensive project documentation
├── requirements.txt                   # Standard library declaration (no 3rd-party dependencies)
├── .gitignore                         # Python, environment, and cache exclusions
│
├── input/                             # Target directory for raw log files
│   ├── .gitkeep
│   ├── server_1.log
│   ├── server_2.log
│   ├── server_3.log
│   ├── server_4.log
│   └── empty.log
│
├── output/                            # Output directory for summary reports
│   ├── .gitkeep
│   └── result.txt                     # Final generated analysis report
│
├── src/                               # Modular source code
│   ├── __init__.py                    # Package initializer
│   ├── main.py                        # Application entry point & CLI parser
│   ├── coordinator.py                 # Pipeline lifecycle coordinator
│   ├── mapper.py                      # Log tokenization & intermediate pair generation
│   ├── shuffle.py                     # Grouping by key & partition routing
│   ├── partitioner.py                 # Deterministic hash partitioner
│   ├── reducer.py                     # Reducer worker aggregation logic
│   ├── input_manager.py               # File discovery, validation & splitting
│   ├── output_manager.py              # Consolidation, sorting & summary reporting
│   └── config.py                      # Centralized configuration dataclass
│
├── tests/                             # Complete unit and integration test suite
│   ├── __init__.py
│   ├── test_input_manager.py          # Member 1 unit tests (discovery, splitting)
│   ├── test_mapper.py                 # Member 1 unit tests (tokenization, mapping)
│   ├── test_coordinator.py            # Member 1 tests (Map stage, workers, metrics)
│   ├── test_partitioner.py            # Member 2 unit tests (hash consistency)
│   ├── test_shuffle.py                # Member 2 unit tests (grouping, partition buckets)
│   ├── test_reducer.py                # Member 2 unit tests (aggregation)
│   └── test_integration.py            # Member 3 integration tests (Tests A-E)
│
├── docs/                              # Technical reports & empirical evaluation
│   ├── architecture.md                # System design & Cloud vs. Local comparison
│   ├── workflow.md                    # Data flow & interface contracts
│   ├── implementation_notes.md        # Concurrency & error handling notes
│   ├── member1_coordinator_map.md     # Member 1 component notes
│   └── experiment_results.md          # Measured benchmark results
│
└── sample_data/                       # Test datasets
    ├── generate_datasets.py           # Reproducible dataset generator script
    ├── benchmark.py                   # Worker-count benchmark (measured, median of runs)
    ├── small/                         # Lightweight test logs (115 KB, 1,000 lines)
    └── medium/                        # Scaled benchmark logs (3.30 MB, 30,000 lines)
```

---

## 4. Requirements

- **Operating System:** Windows 10/11, Linux, or macOS (Tested on Windows 11 AMD64)
- **Runtime:** Python 3.8 or higher (Tested on Python 3.12.10)
- **Dependencies:** Strictly Python Standard Library modules:
  - `multiprocessing` (worker process simulation)
  - `pathlib`, `os` (filesystem operations)
  - `re`, `hashlib` (tokenization & deterministic partitioning)
  - `unittest` (automated testing framework)
  - `time`, `dataclasses`, `collections`, `typing`

---

## 5. Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Rajithan-Pathmanathan/MapReduce-Log-Analyzer.git
   cd MapReduce-Log-Analyzer
   ```

2. **Verify Python environment:**
   ```bash
   python --version
   ```

---

## 6. How to Prepare Input Data

Place your `.log` or `.txt` files directly into `input/`, or use the pre-generated benchmark datasets in `sample_data/`:

```bash
# Re-generate fresh sample datasets at any time:
python sample_data/generate_datasets.py
```

---

## 7. How to Run

Execute the pipeline via the command line:

```bash
# Run with default settings (processes input/ with 4 Map workers, 2 Reduce workers):
python src/main.py

# Run on the medium benchmark dataset:
python src/main.py --input sample_data/medium --map-workers 4 --reduce-workers 2 --top-n 10

# Compare worker counts (prints a Markdown table of measured timings):
python sample_data/benchmark.py
```

Worker counts and `--top-n` must be at least 1. While running, the coordinator prints one line per split, the shuffle partition sizes and one line per reducer, followed by the summary.

---

## 8. Configuration Options

Runtime options can be set via CLI arguments or modified centrally in `src/config.py`:

| Parameter | CLI Flag | Default | Description |
| :--- | :--- | :--- | :--- |
| `input_dir` | `-i`, `--input` | `input/` | Directory containing log files |
| `output_dir` | `-o`, `--output` | `output/` | Directory where output reports are saved |
| `map_workers` | `-m`, `--map-workers` | `4` | Number of parallel Map processes |
| `reduce_workers` | `-r`, `--reduce-workers` | `2` | Number of parallel Reduce processes |
| `top_n_results` | `-t`, `--top-n` | `10` | Number of top frequent keys to display |

---

## 9. Output Description & Verified Results

When the pipeline finishes, the system writes the report to `output/result.txt` (ignored by git). Actual output of `python src/main.py --input sample_data/medium --map-workers 4 --reduce-workers 2`:

```text
MapReduce Log Analysis Results
==============================

Input Files    : 5
Input Size     : 3.2992 MB (3,459,447 bytes)
Map Workers    : 4
Reduce Workers : 2
Input Lines    : 30,000
Input Splits   : 15
Map Output     : 253,868 (term, 1) pairs
Unique Keys    : 84
Keys/Reducer   : [47, 37]
Execution Time : 0.7535 seconds

Phase Breakdown
---------------
Map Phase      : 0.4315 seconds
Shuffle Phase  : 0.0244 seconds
Reduce Phase   : 0.2908 seconds

Top Results
-----------
info                    14909
for                      9986
warning                  7955
error                    6537
inventory-api            6042
payment-gateway          6041
web-frontend             6023
from                     6019
db-cluster               5997
database                 5969
```

Timings vary slightly between runs; counts do not.

---

## 10. Automated Testing

The project includes 61 unit and end-to-end integration test cases covering the complete pipeline:

```bash
# Run all tests using Python standard unittest:
python -m unittest discover -s tests -p "test_*.py"
```

### Verified Test Matrix:
- **Test A (Normal Workload):** Validates repeated term aggregation across multiple log files.
- **Test B (Empty File):** Validates that empty log files are safely handled without throwing exceptions.
- **Test C (Multiple Files):** Validates cross-file aggregation across 4 distinct logs.
- **Test D (Multiple Workers):** Validates execution across 4 Map workers and 3 Reduce workers.
- **Test E (Known Expected Result):** Validates the exact test case from the assignment prompt:
  - File 1: `error error info`
  - File 2: `error warning info`
  - Result: `error = 3`, `info = 2`, `warning = 1`.

---

## 11. Performance Experiment (Measured Results)

`python sample_data/benchmark.py` on `sample_data/medium` (5 files, 3,459,447 bytes, 30,000 lines, 15 splits, 253,868 intermediate pairs, 84 unique keys). Median of 3 runs, Python 3.12.10, Windows 11, 12 logical CPUs:

| Map workers | Reduce workers | Map (s) | Shuffle (s) | Reduce (s) | Total (s) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1 | 0.5166 | 0.0226 | 0.2558 | **0.8011** |
| 2 | 1 | 0.4113 | 0.0236 | 0.2564 | **0.6962** |
| 2 | 2 | 0.4161 | 0.0238 | 0.2628 | **0.7107** |
| 4 | 2 | 0.4451 | 0.0241 | 0.2783 | **0.8137** |
| 8 | 4 | 0.5634 | 0.0247 | 0.3210 | **0.9121** |

**Observation:** 2 Map workers were fastest (Map 0.52 s → 0.41 s). With 4 or 8 workers the job got slower, because on Windows each worker process is started with `spawn` (a fresh interpreter), and at 3.3 MB that start-up cost is larger than the parallel work saved. The Reduce phase (84 keys) is almost entirely process start-up time. Details: `docs/experiment_results.md`.

---

## 11a. Figure 7

Figure 7 must be a real screenshot. Run `python src/main.py --input sample_data/medium --map-workers 4 --reduce-workers 2` in a terminal and capture the window showing the command, the coordinator progress lines and the summary. Caption: **Figure 7: MapReduce program execution and output**.

---

## 12. Limitations (Local Simulation vs. Production Cloud)

1. **Single-Node Resource Contention:** All simulated workers run on one physical machine, sharing CPU cache, RAM bus, and disk bandwidth.
2. **Local File I/O vs. Distributed Storage:** Files are read from local disk; there is no distributed filesystem (e.g., HDFS, Amazon S3) with data block locality.
3. **IPC vs. Network Shuffle:** Data transfer between mappers and reducers occurs via local process pipes rather than distributed HTTP/RPC network shuffles.
4. **Fault Tolerance Scope:** Worker errors are handled via parent process exception handling; real cloud clusters implement node-level heartbeats, task rescheduling, and speculative execution.

---

## 13. Team Division of Responsibilities

| Member | Major Responsibilities | Implemented Components |
| :--- | :--- | :--- |
| **Member 1** – Pavithira Rajkumar | Coordinator + Map Phase | `src/input_manager.py`, `src/mapper.py`, `src/coordinator.py`, `tests/test_input_manager.py`, `tests/test_mapper.py`, `tests/test_coordinator.py` |
| **Member 2** – Dayaleeswaran | Shuffle/Partition + Reduce Phase | `src/partitioner.py`, `src/shuffle.py`, `src/reducer.py`, `tests/test_partitioner.py`, `tests/test_shuffle.py`, `tests/test_reducer.py` |
| **Member 3** – Rajithan Pathmanathan | Integration, Testing, Performance & Docs | `src/output_manager.py`, `src/main.py`, `tests/test_integration.py`, `sample_data/*`, `docs/*`, `README.md`, Figure 7 |
