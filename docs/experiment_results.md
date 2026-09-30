# Performance Experiment & Evaluation Log

**Course:** INTE 22253 – Distributed Systems and Cloud Computing  
**Institution:** University of Kelaniya, Department of Industrial Management  
**Project:** Assignment 01 – Part C – Option 2 (MapReduce Log Analysis System)  
**Lead Evaluator:** Member 3 (Integration + Testing + Documentation)

---

## 1. Experimental Environment Specification

- **Processor (CPU):** Intel64 Family 6 Model 165 Stepping 2, GenuineIntel (12 Logical Cores)
- **Host Operating System:** Microsoft Windows 11 (Build 10.0.22631)
- **Python Runtime:** Python 3.12.10 (AMD64 64-bit)
- **Process Worker Model:** Python standard library `multiprocessing` (Process Pool, `spawn` start method)
- **Storage Subsystem:** Local NVMe SSD (NTFS filesystem)

---

## 2. Benchmark Dataset Profiles

| Dataset Profile | Directory Path | File Count | Total Size (Bytes) | Total Size (MB) | Total Lines | Description |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Small Dataset** | `sample_data/small/` | 5 | 115,380 | 0.1100 MB | 1,000 | Quick verification & edge cases (includes 1 empty file) |
| **Medium Dataset** | `sample_data/medium/` | 5 | 3,459,447 | 3.2992 MB | 30,000 | Realistic multi-MB workload for concurrency scaling |

---

## 3. Worker Scaling (Measured)

Produced by `python sample_data/benchmark.py` (medium) and `python sample_data/benchmark.py --input sample_data/small`. Each row is the median of 3 runs of the full pipeline. The script also checks that every run and every configuration produced identical counts.

### Medium dataset – 15 splits, 253,868 intermediate pairs, 84 unique keys

| Map workers | Reduce workers | Map (s) | Shuffle (s) | Reduce (s) | Total (s) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1 | 0.5166 | 0.0226 | 0.2558 | **0.8011** |
| 2 | 1 | 0.4113 | 0.0236 | 0.2564 | **0.6962** |
| 2 | 2 | 0.4161 | 0.0238 | 0.2628 | **0.7107** |
| 4 | 2 | 0.4451 | 0.0241 | 0.2783 | **0.8137** |
| 8 | 4 | 0.5634 | 0.0247 | 0.3210 | **0.9121** |

### Small dataset – 4 splits (the empty file produces none), 8,478 intermediate pairs, 84 unique keys

| Map workers | Reduce workers | Map (s) | Shuffle (s) | Reduce (s) | Total (s) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1 | 0.2668 | 0.0008 | 0.2580 | **0.5303** |
| 2 | 1 | 0.2763 | 0.0009 | 0.2585 | **0.5373** |
| 2 | 2 | 0.2809 | 0.0009 | 0.2742 | **0.5619** |
| 4 | 2 | 0.3282 | 0.0012 | 0.2787 | **0.6088** |
| 8 | 4 | 0.3266 | 0.0011 | 0.3172 | **0.6499** |

---

## 4. Top Results (Medium Dataset, 4 Map / 2 Reduce)

From `output/result.txt`. Timestamps, IP octets and status codes are not counted as terms (Member 1 tokenisation rule).

| Rank | Term | Count |
| :---: | :--- | :---: |
| 1 | `info` | 14,909 |
| 2 | `for` | 9,986 |
| 3 | `warning` | 7,955 |
| 4 | `error` | 6,537 |
| 5 | `inventory-api` | 6,042 |
| 6 | `payment-gateway` | 6,041 |
| 7 | `web-frontend` | 6,023 |
| 8 | `from` | 6,019 |
| 9 | `db-cluster` | 5,997 |
| 10 | `database` | 5,969 |

---

## 5. Observations for the Report

1. **Parallel Map helps up to 2 workers on the medium set.** Map time fell from 0.5166 s (1 worker) to 0.4113 s (2 workers), about 20% faster, and total time from 0.8011 s to 0.6962 s.
2. **More workers were slower at this size.** 4 and 8 Map workers took 0.4451 s and 0.5634 s. On Windows every worker is started with `spawn` (a new Python interpreter that re-imports the project), and the intermediate pairs are pickled back to the coordinator. At 3.3 MB that fixed cost outweighs the extra parallelism.
3. **Reduce time is mostly process start-up.** Only 84 keys are summed, yet the phase takes about 0.26–0.32 s and grows with the reducer count, so it measures pool creation rather than aggregation work.
4. **Small dataset shows no speed-up at all.** 1,000 lines are split into only 4 splits, so the 1-worker run is the fastest (0.5303 s).
5. **Shuffle is cheap** (≈0.02 s for 253,868 pairs) because it is an in-memory group-by inside the coordinator process; in a real cluster this step moves data over the network and is usually the most expensive.
6. **Correctness does not depend on worker count:** all 10 configurations produced identical counts.

More workers would be expected to pay off on a much larger dataset, where Map work dominates the fixed process cost; that was not measured here.
