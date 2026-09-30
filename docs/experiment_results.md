# Performance Experiment & Evaluation Log

**Module:** INTE 22253 – Distributed Systems and Cloud Computing  
**Project:** MapReduce Log Analysis System  
**Lead Evaluator:** Member 3 (Integration + Testing + Documentation)

---

> [!IMPORTANT]
> **Academic Integrity Notice:**  
> In accordance with university project regulations, **no benchmark numbers or execution times are fabricated**.  
> The tables below serve as the designated recording template. Measurements will be collected and recorded only after the implementation is integrated and benchmark runs are executed on real hardware.

---

## 1. Experimental Environment Specification

- **Processor (CPU):** *To be recorded upon execution*
- **Physical Cores / Threads:** *To be recorded upon execution*
- **Installed Memory (RAM):** *To be recorded upon execution*
- **Operating System:** Windows
- **Python Version:** *To be recorded upon execution*
- **Storage Type:** Local SSD / HDD

---

## 2. Benchmark Dataset Profiles

| Dataset Profile | Directory Path | File Count | Total Size (MB) | Total Lines | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Small Dataset** | `sample_data/small/` | *Pending Run* | *Pending Run* | *Pending Run* | Quick correctness and unit testing |
| **Medium Dataset** | `sample_data/medium/` | *Pending Run* | *Pending Run* | *Pending Run* | Concurrency and scaling evaluation |

---

## 3. Worker Scaling Performance Matrix

Experimental runs evaluating execution time against varying parallel worker counts:

| Run # | Map Workers | Reduce Workers | Dataset | Total Input Size | Unique Keys | Map Phase Time (s) | Shuffle Phase Time (s) | Reduce Phase Time (s) | Total Wall-Clock Time (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 1 | 1 | Medium | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |
| 2 | 2 | 1 | Medium | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |
| 3 | 4 | 2 | Medium | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |

---

## 4. Key Observations & Scaling Analysis

*(To be written following actual benchmark runs)*

- **Speedup Analysis:** Evaluate whether increasing worker count yielded linear, sublinear, or negative speedup.
- **Overhead Factors:** Analyze Python process spawning latency and inter-process communication (IPC) serialization costs on smaller datasets.
- **Bottlenecks:** Identify whether the job is I/O-bound (reading disk files) or CPU-bound (tokenization and sorting).
