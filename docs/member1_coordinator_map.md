# Member 1 – Coordinator & Map Phase

**Module:** INTE 22253 – Distributed Systems and Cloud Computing
**Component:** Coordinator + Map Phase (`src/coordinator.py`, `src/mapper.py`, `src/input_manager.py`)

---

## Component Diagram

```
Input Directory (*.log / *.txt)
        │
        ▼
  ┌─────────────┐
  │ InputManager │  validate_directory()
  │             │  discover_files()
  │             │  measure_input()
  └──────┬──────┘
         │ List[Path]
         ▼
  ┌─────────────────────┐
  │  create_byte_splits  │  cuts each file into [start, end) byte ranges
  └──────────┬──────────┘
             │ List[InputSplit]
             ▼
  ┌─────────────────────────────────────────┐
  │           Coordinator                   │
  │  multiprocessing.Pool(num_workers)      │
  │  pool.imap(map_split_worker, splits, 1) │  ← dynamic split assignment
  └─────────────┬───────────────────────────┘
                │ per-split result dicts
                ▼
  ┌──────────────────────┐
  │  Flatten & sort by   │  Interface A: List[Tuple[str, int]]
  │  split_id            │  e.g. [("error",1), ("database",1), ...]
  └──────────┬───────────┘
             │
             ▼
    Member 2 → ShuffleManager.shuffle_and_partition()
```

---

## 1. Input Discovery and Measurement

`InputManager` (src/input_manager.py) is responsible for all input-related operations.

### Discovery
`discover_files(patterns=("*.log","*.txt"))` globs both patterns and returns a **sorted, de-duplicated** list of `Path` objects. No file names are hard-coded.

### Validation
`validate_directory()` raises:
- `FileNotFoundError` – directory does not exist
- `NotADirectoryError` – path is not a directory
- `ValueError` – directory contains no `.log` or `.txt` files

### Measurement
`measure_input(files)` returns:
```python
{
    "file_count":   int,
    "total_bytes":  int,
    "total_lines":  int,
    "files": [{"file": str, "bytes": int, "lines": int}, ...]
}
```
Line counting uses 1 MiB binary blocks (`count_lines`). A file that ends without `\n` still counts its last line.

---

## 2. Byte-Range Input Splits

`create_byte_splits(files, split_size)` cuts each file into `InputSplit` objects:

```python
@dataclass(frozen=True)
class InputSplit:
    split_id: int   # global 0..n-1 counter
    path: Path
    start: int      # first byte (inclusive)
    end: int        # one past the last byte
```

- Empty files produce **no splits**.
- `split_size < 1` raises `ValueError`.
- `split_id` runs continuously across all files so results can be sorted deterministically.
- Default: `256 KiB` (`DEFAULT_SPLIT_SIZE_BYTES = 256 * 1024`), configurable via `Config.split_size_bytes`.

---

## 3. Line-Boundary Rule

`read_split_lines(path, start, end)` implements the same rule Hadoop's `LineRecordReader` uses:

> **A split owns every line whose first byte lies in `[start, end)`.**

```python
with open(path, "rb") as f:
    if start > 0:
        f.seek(start - 1)
        f.readline()      # discard partial line → belongs to previous split
    pos = f.tell()
    while pos < end:
        raw = f.readline()
        if not raw:
            break
        pos += len(raw)
        yield raw.decode("utf-8", errors="replace")
```

This guarantees every line is processed by **exactly one** split, regardless of where the byte boundary falls.

---

## 4. Dynamic Split Assignment

`run_map_phase(splits)` uses:
```python
with Pool(processes=num_workers) as pool:
    results = list(pool.imap(worker_fn, splits, chunksize=1))
```

`chunksize=1` means each worker fetches one split at a time. When a worker finishes early it immediately receives the next unprocessed split — a simple form of **dynamic task scheduling** that prevents slow workers from becoming a bottleneck.

---

## 5. Worker Count

`determine_map_worker_count(n_splits)` returns:
```
workers = config.map_workers  (or cpu_count() if 0/None)
workers = min(workers, n_splits)   # never more workers than splits
workers = max(1, workers)          # always at least 1
```

---

## 6. Timing

The Map phase is timed with `time.perf_counter()`:
```python
t_map = time.perf_counter()
intermediate = self.run_map_phase(splits)
self.metrics["map_time_seconds"] = time.perf_counter() - t_map
```

Metrics recorded: `input_files_count`, `total_input_bytes`, `total_input_lines`, `split_count`, `intermediate_pairs`, `map_worker_processes_used`, `lines_mapped`, `map_time_seconds`.

---

## 7. Tokenisation Rules

**Pattern:**
```python
TOKEN_PATTERN = re.compile(r"(?<![a-z0-9_-])[a-z][a-z0-9_-]*")
```

Rules:
1. Line is lowercased (unless `case_sensitive=True`).
2. A token **must start with a letter** at a word boundary (negative look-behind blocks `[a-z0-9_-]`).
3. After the leading letter, `a-z`, `0-9`, `_` and `-` are allowed.
4. Tokens shorter than `min_word_length` (default 2) are dropped.

**Example:**
```
Input:  "2026-09-30T14:02:11.000Z 192.168.1.10 INFO payment-gateway 200 OK"
Output: [("info",1), ("payment-gateway",1), ("ok",1)]
```
Numbers (`2026`, `192`, `168`, `000z`), IP octets and timestamps are **not** tokens.

---

## 8. How to Run

### Run the full job
```bash
# From the repository root
python src/main.py --input input --map-workers 4 --reduce-workers 2
```

### Run with sample data
```bash
python src/main.py --input sample_data/medium --map-workers 2 --reduce-workers 2
```

### Run tests (Member 1 scope)
```bash
python -m unittest tests.test_input_manager tests.test_mapper tests.test_coordinator -v
```

### Run all tests
```bash
python -m unittest discover -s tests -v
```

Expected: top results are real words (`info`, `warning`, `error`, ...) — **not** numbers like `000z`, `168` or `192`.
