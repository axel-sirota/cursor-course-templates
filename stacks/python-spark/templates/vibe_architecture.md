# Architecture Vibe: Python Spark

This document answers the "which tool?" questions that come up repeatedly in data engineering. Use it to make technology decisions confidently.

---

## When Spark over pandas

Use Spark when:
- Data exceeds available RAM (typically > 10GB per partition or > 100GB total)
- You need distributed shuffle across nodes
- You need Delta ACID semantics on writes (concurrent writers, schema enforcement, time travel)
- The pipeline runs on a schedule in Databricks, EMR, or a managed Spark cluster
- You need Structured Streaming for near-real-time processing

Use pandas when:
- Data fits comfortably in memory (< 1GB)
- The transform is a one-off analysis or prototype
- You are building an ML model on a sample, not scoring at scale
- Spark adds complexity without a measurable benefit

**Rule of thumb**: if it runs fast enough in pandas and doesn't need ACID writes, use pandas. Spark is a tool for scale, not a default.

---

## Medallion vs Star Schema

These are not alternatives — they operate at different levels.

**Medallion** (Bronze → Silver → Gold) is the **operational pipeline structure** — how data flows through quality layers. It describes data movement and transformation stages.

**Star Schema** (facts + dimensions) is the **Gold layer's internal design** — how business analysts query it. A Gold layer is often implemented as a Star Schema.

Think of it this way: Medallion is the highway system, Star Schema is the city layout at the destination.

---

## Spark vs dbt

| | Spark | dbt |
|---|---|---|
| Language | Python + SQL | SQL only |
| Engine | Distributed compute (Spark) | Warehouse engine (Snowflake, BigQuery, Redshift) |
| Strengths | Python transforms, ML features, streaming, complex UDFs | SQL-first modeling, lineage, testing, analytics engineering |
| Weakness | Overkill for pure SQL transforms | Cannot run Python logic natively |

Use Spark for:
- Python-heavy transforms (regex, ML scoring, custom logic)
- Feature engineering at scale
- Streaming pipelines
- When you are already on Databricks

Use dbt for:
- SQL-first analytics modeling
- When lineage and documentation matter to the analytics team
- When the warehouse is the compute engine (Snowflake, BigQuery)

They are often used together: Spark writes Silver Delta tables, dbt models Gold analytics tables on top.

---

## Delta Lake vs Parquet

| | Parquet | Delta Lake |
|---|---|---|
| ACID transactions | No | Yes |
| Schema enforcement | No | Yes (configurable) |
| Time travel | No | Yes (versioned) |
| DML (UPDATE/DELETE/MERGE) | No | Yes |
| Concurrent writes | Unsafe | Safe |
| File compaction | Manual | OPTIMIZE command |

**Rule**: Use Delta Lake for any table you write to more than once. Raw Parquet is acceptable for immutable Bronze archives where you never UPDATE or MERGE — but even then, Delta adds minimal overhead and future-proofs the table.

---

## Structured Streaming vs Batch

Use **Structured Streaming** when:
- Latency requirement is sub-minute
- Source is Kafka, Kinesis, or Event Hubs
- You need exactly-once semantics with stateful aggregations

Use **batch** (Databricks Workflows trigger) when:
- Hourly or daily data freshness is acceptable
- Data arrives in files (S3, ADLS, GCS)
- Simplicity matters — streaming adds stateful complexity

**Rule**: default to batch. Adopt streaming only when a business requirement cannot be met by batch. The operational overhead of streaming is real.

---

## PySpark vs Scala Spark

Default to **PySpark**:
- Larger community, more libraries, faster iteration
- pandas_udf (vectorized UDFs) closes most performance gaps
- MLlib, MLflow, and most Databricks features are Python-first

Use **Scala** only when:
- Python performance is demonstrably insufficient after profiling
- You are writing a custom Spark extension or connector
- The team has strong Scala expertise and the project justifies the investment

**Rule**: Python first. Measure performance before switching. The gap is smaller than it used to be.
