# Local MapReduce Log Analysis System

**Course:** INTE 22253 – Distributed Systems and Cloud Computing  
**Institution:** University of Kelaniya, Faculty of Science, Department of Industrial Management  
**Project:** Assignment 01 – Part C – Option 2 (MapReduce Log Analysis System)  

---

## 1. Project Purpose

Modern IT and enterprise applications generate continuous streams of semi-structured log files across multiple servers. Ingestion and analysis of these logs (e.g., aggregating frequency of error occurrences, warning events, and system accesses) quickly becomes a processing bottleneck when executed sequentially on a single thread.

This project implements a **local, multi-process MapReduce log analysis pipeline** in Python. The system simulates distributed Map and Reduce workers on a multi-core machine using the Python `multiprocessing` library. The primary academic objectives are:
- Demonstrate core MapReduce programming abstractions: input splitting, map transformation, deterministic shuffle/partitioning, parallel reduction, and result aggregation.
- Measure performance characteristics (wall-clock execution time and throughput) across different worker configurations.
- Compare and contrast local multi-process simulation against real-world distributed cloud platforms (e.g., Apache Hadoop, AWS EMR).

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
                         │ (Deterministic Routing)
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
1. **Input Splitting:** `InputManager` discovers raw log files in `input/` and partitions them into balanced subsets.
2. **Map Phase:** Multiple parallel `Map` worker processes read assigned splits, tokenize log entries into normalized terms, and emit intermediate key-value pairs `(term, 1)`.
3. **Shuffle & Partition Phase:** `ShuffleManager` groups intermediate values by unique key (`term -> [1, 1, ...]`), and `Partitioner` applies deterministic hashing (`hash(term) % num_reducers`) to assign each key exclusively to one reducer partition.
4. **Reduce Phase:** Multiple parallel `Reduce` worker processes aggregate counts for each assigned key (`term -> total_count`).
5. **Output Generation:** `OutputManager` consolidates reduced results, sorts terms by descending frequency, displays a terminal summary (for academic report verification), and writes results to disk.

---

## 3. Project Structure

```text
MapReduce-Log-Analyzer/
│
├── README.md                   # Complete project documentation and guide
├── requirements.txt            # Dependency specification (standard library only)
├── .gitignore                  # Git exclusions for Python artifacts & output
│
├── input/                      # Input directory for target log files
│   └── .gitkeep
│
├── output/                     # Output directory for analysis reports
│   └── .gitkeep
│
├── src/                        # Modular source code
│   ├── __init__.py             # Package initializer
│   ├── main.py                 # Application CLI entry point
│   ├── coordinator.py          # MapReduce workflow coordinator
│   ├── input_manager.py        # File discovery, validation, and splitting
│   ├── mapper.py               # Map worker tokenization & key-value emission
│   ├── partitioner.py          # Deterministic key-to-reducer routing
│   ├── shuffle.py              # Intermediate grouping & partition staging
│   ├── reducer.py              # Reduce worker aggregation logic
│   ├── output_manager.py       # Result consolidation, formatting & export
│   └── config.py               # Centralized configuration settings
│
├── tests/                      # Unit and integration test suite
│   ├── __init__.py
│   ├── test_input_manager.py   # Unit tests for input discovery & splitting
│   ├── test_mapper.py          # Unit tests for map tokenization
│   ├── test_partitioner.py     # Unit tests for deterministic routing
│   ├── test_shuffle.py         # Unit tests for intermediate grouping
│   ├── test_reducer.py         # Unit tests for reduce aggregation
│   └── test_integration.py     # End-to-end pipeline integration tests
│
├── docs/                       # Technical reports and evaluation templates
│   ├── architecture.md         # Detailed architectural documentation
│   ├── workflow.md             # Development workflow & interface contracts
│   ├── implementation_notes.md # Technical guidelines & error handling
│   └── experiment_results.md   # Empirical benchmark log (no fabricated data)
│
└── sample_data/                # Sample datasets for testing & benchmarking
    ├── small/                  # Lightweight test logs (< 1 MB)
    └── medium/                 # Benchmark evaluation logs (5 - 20 MB)
```

---

## 4. Requirements

- **Operating System:** Windows 10/11, Linux, or macOS
- **Runtime:** Python 3.8 or higher
- **Dependencies:** None. The project relies strictly on the **Python Standard Library** (`multiprocessing`, `pathlib`, `os`, `re`, `hashlib`, `unittest`, `dataclasses`, `time`).

---

## 5. Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd MapReduce-Log-Analyzer
   ```

2. **Verify Python environment:**
   ```bash
   python --version
   ```

3. *(Optional)* Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

---

## 6. How to Prepare Input Data

Place your `.log` or `.txt` files directly into the `input/` folder, or point to one of the directories in `sample_data/`:

```bash
# Example structure:
input/
├── server_alpha.log
├── server_beta.log
└── application.log
```

---

## 7. How to Run

Execute the pipeline via the command line:

```bash
# Run with default settings (processes files in input/):
python src/main.py

# Run with custom worker concurrency and input directory:
python src/main.py --input sample_data/small --map-workers 4 --reduce-workers 2 --top-n 15
```

---

## 8. Configuration Options

Runtime options can be set via command-line arguments or modified centrally in `src/config.py`:

| Parameter | CLI Flag | Default | Description |
| :--- | :--- | :--- | :--- |
| `input_dir` | `-i`, `--input` | `input/` | Directory containing log files |
| `output_dir` | `-o`, `--output` | `output/` | Directory where output reports are saved |
| `map_workers` | `-m`, `--map-workers` | `4` | Number of parallel Map processes |
| `reduce_workers` | `-r`, `--reduce-workers` | `2` | Number of parallel Reduce processes |
| `top_n_results` | `-t`, `--top-n` | `10` | Number of top frequent keys to display |

---

## 9. Output Description

Upon successful execution, the system produces:
1. **A formatted console summary** detailing dataset statistics, worker allocation, execution timing per stage, and Top-N frequent terms. This output is formatted specifically to provide clean verification for the university report (Figure 7 requirement).
2. **A persistent report file** saved to `output/analysis_summary.txt`.

---

## 10. Testing

Run all unit and integration tests using Python's built-in `unittest` runner:

```bash
# Run the entire test suite:
python -m unittest discover -s tests -p "test_*.py"

# Run a specific test module:
python -m unittest tests/test_partitioner.py
```

---

## 11. Performance Experimentation

To evaluate scaling characteristics, benchmark runs will be performed across varying worker counts (e.g., 1 vs 2 vs 4 workers) on the same dataset.

Actual wall-clock execution times, phase durations, and unique key counts will be collected empirically and logged directly into `docs/experiment_results.md`. **No synthetic or fabricated benchmark results are used.**

---

## 12. Limitations (Simulation vs. Production Cloud)

1. **Shared Compute & Memory:** All simulated workers share one machine's CPU cores and RAM bus, unlike multi-node clusters with isolated hardware resources.
2. **Local Storage I/O:** Reading from local disk avoids network transport overhead but introduces local disk I/O contention. Real distributed systems leverage distributed filesystems (HDFS, Amazon S3) with data locality optimizations.
3. **IPC vs. Network Shuffle:** Inter-worker data transfer utilizes local memory/process pipes rather than high-throughput distributed network shuffle protocols.
4. **Fault Tolerance Scope:** In this simulation, worker process exceptions are caught locally by the parent process; production clusters implement cluster-wide heartbeat monitors, node-level failover, and speculative execution.

---

## 13. Team Responsibilities

The codebase is partitioned into three distinct, non-overlapping workstreams:

| Team Member | Core Focus | Primary Source Files | Primary Test Files |
| :--- | :--- | :--- | :--- |
| **Member 1** | Coordinator + Map Phase | `src/coordinator.py`<br>`src/input_manager.py`<br>`src/mapper.py` | `tests/test_input_manager.py`<br>`tests/test_mapper.py` |
| **Member 2** | Shuffle/Partition + Reduce Phase | `src/partitioner.py`<br>`src/shuffle.py`<br>`src/reducer.py` | `tests/test_partitioner.py`<br>`tests/test_shuffle.py`<br>`tests/test_reducer.py` |
| **Member 3** | Integration + Testing + Documentation | `src/main.py`<br>`src/output_manager.py` | `tests/test_integration.py`<br>`docs/*`<br>`README.md` |
