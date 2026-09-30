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
- **Line Normalization:**
  - Strip surrounding whitespace.
  - Lowercase all tokens (case-insensitive aggregation).
  - Extract alphanumeric tokens using regex `r"\b[a-zA-Z0-9_-]+\b"`.
  - Filter out tokens shorter than `min_word_length` (e.g., length < 2).
  - Discard empty tokens.

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
