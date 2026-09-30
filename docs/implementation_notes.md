# Implementation Notes & Technical Guidelines

**Module:** INTE 22253 – Distributed Systems and Cloud Computing  
**Project:** MapReduce Log Analysis System

---

## 1. Concurrency Simulation with Python Multiprocessing

### Process-Based Workers vs. Threads
- In standard CPython, the **Global Interpreter Lock (GIL)** prevents multiple native threads from executing Python bytecodes concurrently on multiple CPU cores.
- To accurately simulate distributed workers on multi-core systems, we use the standard library `multiprocessing` module (`multiprocessing.Pool` or `multiprocessing.Process`).
- Each worker runs in its own memory space, mirroring how separate physical/virtual nodes execute without shared memory in a distributed cluster.

### Windows OS Process Spawning Model
- On Windows, Python uses the `spawn` start method rather than `fork`. This means child processes re-import the main module.
- **Rule:** All process creation and top-level execution calls must be guarded behind `if __name__ == '__main__':` and `multiprocessing.freeze_support()` in `src/main.py`. Failure to do so causes infinite process spawning loops on Windows.

---

## 2. Deterministic Partitioning Mechanism

### Why Python's Built-in `hash()` is Unsuitable
- Since Python 3.3, Python employs randomized hash seed randomization (SIPHASH) across separate process invocations for security reasons (`PYTHONHASHSEED`).
- As a consequence, `hash("error")` evaluated in Process A might yield a different integer than in Process B, violating partition consistency.

### Solution: Cryptographic / Digest Hashing
- Member 2's `Partitioner` will use a stable hash algorithm such as `hashlib.md5` or `hashlib.sha256`:
  ```python
  import hashlib

  def deterministic_hash(key: str) -> int:
      return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
  ```
- This guarantees that identical keys always map to the exact same partition index across all processes and runs.

---

## 3. Data Processing & Tokenization Rules

- **Input Format:** Standard text files (`.log`, `.txt`) containing server logs (e.g., Apache, Nginx, application server logs).
- **Line Normalization** (`src/mapper.py`):
  - Lowercase the line (unless `case_sensitive=True`).
  - Extract tokens with `(?<![a-z0-9_-])[a-z][a-z0-9_-]*`: a token must start with a letter,
    so timestamps, IP octets and status codes are not counted; `db_pool`, `http2`,
    `payment-gateway` are kept whole.
  - Drop tokens shorter than `min_word_length` (default 2).
  - Blank lines emit nothing.

---

## 3a. Coordinator + Map Phase (Member 1)

**Flow** (`Coordinator.run_map_stage()`):

1. `InputManager.validate_directory()` / `discover_files()` – finds every `*.log` / `*.txt` in the input directory (no hard-coded names).
2. `InputManager.measure_input()` – real file count, bytes and line count, stored in `Coordinator.metrics`.
3. `create_byte_splits(files, config.split_size_bytes)` – cuts each file into byte ranges (default 256 KiB). Empty files produce no splits.
4. `run_map_phase(splits)` – a `multiprocessing.Pool` of `min(map_workers, len(splits))` processes runs `map_split_worker` on each split. A worker opens the file itself and reads only its range; a line belongs to the split containing its first byte, so no line is lost or counted twice.
5. Map time is measured with `time.perf_counter()` into `metrics["map_time_seconds"]`.

**Interface to Member 2:** `run_map_stage()` returns a flat `List[Tuple[str, int]]`, e.g. `[("error", 1), ("database", 1), ...]`, ordered by split id. `execute_job()` passes it straight to `ShuffleManager.shuffle_and_partition()`.

**Metrics recorded:** `input_files_count`, `total_input_bytes`, `total_input_lines`, `input_splits`, `map_workers`, `map_worker_pids`, `intermediate_pairs`, `map_time_seconds`.

**Tests:** `python -m unittest tests.test_coordinator tests.test_mapper tests.test_input_manager`

---

## 4. Error Handling Strategy

The system enforces fail-safe validation with clear diagnostic messages:

| Scenario | Handling Strategy |
| :--- | :--- |
| **Missing Input Directory** | Raise `FileNotFoundError` with clear path guidance before job initialization. |
| **Empty Input Directory** | Raise `ValueError` indicating no matching `.log` files found. |
| **Empty Input File** | Handled gracefully: emits an empty list of intermediate pairs without failing the job. |
| **Unreadable File / Permission Error** | Log error message with file path; skip or raise descriptive exception depending on configuration. |
| **Invalid Worker Configuration** | Enforce `map_workers >= 1` and `reduce_workers >= 1` during configuration parsing. |
| **Worker Process Failure** | Captured by parent process via exception handling in multiprocessing workers. |
