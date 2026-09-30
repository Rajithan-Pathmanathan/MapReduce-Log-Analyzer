# System Architecture: MapReduce Log Analysis System

**Module:** INTE 22253 – Distributed Systems and Cloud Computing  
**Institution:** University of Kelaniya, Faculty of Science, Department of Industrial Management  
**Project:** Part C – Option 2 (MapReduce Log Analysis System)

---

## 1. Architectural Overview

The system implements the **MapReduce programming model** to process and analyze semi-structured server and application log files. It divides data processing into distinct phases: input splitting, parallel mapping, intermediate key-value grouping, deterministic partitioning, parallel reduction, and final aggregation.

```
                    INPUT LOG FILES
                         |
                         v
                    COORDINATOR
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          MAPPER 1    MAPPER 2    MAPPER N
             |           |           |
             +-----------+-----------+
                         |
                         v
                SHUFFLE / PARTITION
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          REDUCER 1   REDUCER 2   REDUCER N
             |           |           |
             +-----------+-----------+
                         |
                         v
                    FINAL OUTPUT
```

---

## 2. Core Components

1. **Coordinator (`src/coordinator.py`):**
   - Orchestrates the full lifecycle of the MapReduce job.
   - Delegates input splitting to `InputManager`.
   - Dispatches tasks to parallel Map workers.
   - Hands intermediate key-value streams over to `ShuffleManager`.
   - Dispatches partitions to parallel Reduce workers.
   - Measures wall-clock execution times across phases.

2. **Input Manager (`src/input_manager.py`):**
   - Scans and validates input log files.
   - Computes total dataset size.
   - Divides files into balanced input splits.

3. **Map Workers (`src/mapper.py`):**
   - Execute in parallel worker processes via Python `multiprocessing`.
   - Tokenize log lines and normalize terms (case folding, punctuation stripping).
   - Emit intermediate key-value pairs: `(term, 1)`.

4. **Shuffle & Partitioner (`src/shuffle.py`, `src/partitioner.py`):**
   - Collects intermediate pairs from all Map workers.
   - Groups values by unique key: `key -> [1, 1, 1, ...]`.
   - Uses a deterministic hash function (`MD5(key) % num_reducers`) to assign each key to a specific reducer partition, ensuring all occurrences of a key go to the same reducer.

5. **Reduce Workers (`src/reducer.py`):**
   - Execute in parallel worker processes.
   - Aggregate occurrences for each assigned key (e.g., `sum(values)`).
   - Emit consolidated `(key, total_count)` tuples.

6. **Output Manager (`src/output_manager.py`):**
   - Consolidates reducer outputs.
   - Sorts results by frequency (descending order).
   - Generates formatted terminal reports and persistent output files.

---

## 3. Local Simulation vs. Real Cloud Deployment

> [!IMPORTANT]
> This system is a **local simulation** of distributed computing. It is designed to illustrate and validate the MapReduce model without requiring a multi-node cluster.

The table below contrasts our local simulated architecture with a real-world cloud deployment (e.g., Apache Hadoop on AWS EMR or Google Cloud Dataproc):

| Dimension | Local Simulation (Our Implementation) | Real Cloud Cluster (e.g., Hadoop / AWS EMR) |
| :--- | :--- | :--- |
| **Compute Infrastructure** | Single physical machine with multi-core CPU. | Clustered fleet of independent virtual machines (EC2 instances / worker nodes). |
| **Worker Abstraction** | Operating system processes (`multiprocessing.Process` / `Pool`). | Distributed worker daemons running inside separate VMs or containers. |
| **Storage Architecture** | Local filesystem (NTFS / ext4). | Distributed file system (HDFS, Amazon S3, Google Cloud Storage). |
| **Data Locality** | All processes read from the same local disk bus. | Computation is scheduled where data blocks reside (rack awareness, block replica locality). |
| **Shuffle Mechanism** | In-memory grouping and IPC inter-process queues/pipes. | High-throughput network shuffle (HTTP transfer, RPC, disk spilling). |
| **Fault Tolerance** | Parent process handles worker exceptions locally. | Heartbeats, automatic worker rescheduling, task speculative execution, checkpointing. |
| **Scalability** | Vertical only (bounded by CPU cores and RAM of host). | Horizontal (scale out to hundreds or thousands of compute nodes). |

---

## 4. Key MapReduce Invariants

- **Partition Invariant:** For any job, every intermediate pair with key $k$ must be routed to partition $p = \text{hash}(k) \pmod R$, where $R$ is the number of reducers.
- **Completeness:** All input records must be consumed by mappers, and all emitted map pairs must reach a reducer.
- **Determinism:** Given identical input files and worker configurations, the final aggregated counts must be identical across runs.
