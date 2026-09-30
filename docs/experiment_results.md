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

## 3. Worker Scaling Performance Matrix (Actual Empirical Measurements)

The following metrics represent actual wall-clock timings captured on the test hardware. **No fabricated or simulated values are used.**

| Run # | Map Workers | Reduce Workers | Dataset | Total Input Size | Unique Keys | Map Phase (s) | Shuffle Phase (s) | Reduce Phase (s) | Total Wall-Clock Time (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Run 1** | 1 | 1 | Medium (30k lines) | 3.2992 MB | 152 | 0.6388 s | 0.0396 s | 0.1278 s | **0.8076 s** |
| **Run 2** | 2 | 1 | Medium (30k lines) | 3.2992 MB | 152 | 0.4745 s | 0.0374 s | 0.1285 s | **0.6418 s** |
| **Run 3** | 4 | 2 | Medium (30k lines) | 3.2992 MB | 152 | 0.4215 s | 0.0519 s | 0.1562 s | **0.6312 s** |

---

## 4. Top Key-Value Aggregation Results (From Medium Benchmark)

| Rank | Token / Event Key | Aggregated Count | Semantic Description |
| :---: | :--- | :---: | :--- |
| 1 | `000z` | 30,000 | ISO timestamp millisecond suffix |
| 2 | `168` | 30,000 | Subnet IP octet prefix |
| 3 | `192` | 30,000 | Private class C IP octet prefix |
| 4 | `2026-09-30t14` | 30,000 | Timestamp date and hour prefix |
| 5 | `info` | 14,909 | Informational severity log events |
| 6 | `for` | 9,986 | Common message preposition token |
| 7 | `warning` | 7,955 | Warning severity log alerts |
| 8 | `error` | 6,537 | System error level events |
| 9 | `inventory-api` | 6,042 | Microservice component identifier |
| 10 | `payment-gateway` | 6,041 | Payment gateway service identifier |

---

## 5. Scaling Observations & Analysis for Academic Report

1. **Map Phase Parallel Speedup:**
   - Moving from 1 Map worker to 2 Map workers decreased Map phase duration from **0.6388s to 0.4745s** (a ~25.7% latency reduction).
   - Expanding to 4 Map workers further reduced Map phase runtime to **0.4215s** (a ~34.0% cumulative reduction over single-worker baseline).
   
2. **Diminishing Returns & Multiprocessing Overhead:**
   - On Windows, worker processes are spawned rather than forked, incurring process initialization, IPC serialization (pickling/unpickling input splits and intermediate tuples), and inter-process communication overhead.
   - For a 3.3 MB dataset, spawning 4 Map processes and 2 Reduce processes introduced slight IPC overhead in the shuffle/reduce stages (0.0519s and 0.1562s respectively).
   - This empirical observation demonstrates a key distributed systems principle: *Parallelization benefits are non-linear on small-to-medium local workloads due to coordination and IPC costs.*
