# Session 11 — New Stack: `python-spark`

**Phase:** 3 — Group C (data-scientist persona)
**Parallel with:** Sessions 7, 8, 9, 10, 12
**Depends on:** Sessions 1–6 complete
**Client fit:** Data engineering teams, Databricks customers, any team building large-scale ETL/ELT pipelines

## Architecture Shape
Data Pipeline — PySpark transformations on distributed data. Databricks Runtime or open-source Spark. Delta Lake for ACID storage. Not a web API. Not a notebook (use python-datascience for exploration).

---

## Files to Create

```
stacks/python-spark/
├── context.md
├── rules/
│   ├── 000-spark-workflow.mdc
│   ├── 100-spark-architecture.mdc
│   ├── 200-spark-testing.mdc
│   └── 300-spark-style.mdc
├── templates/
│   ├── spark-starter.md
│   ├── phase-checklist.md
│   └── job-config.yml
├── vibe/
│   ├── vibe_architecture.md
│   └── vibe_development_lifecycle.md
└── examples/
    └── sales-pipeline/
        ├── jobs/
        │   ├── ingest.py
        │   └── transform.py
        ├── tests/
        │   ├── conftest.py
        │   └── test_transform.py
        └── configs/
            └── job.yml
```

---

## File Specifications

### `context.md`

```markdown
# Project Context: Python Spark

## Tech Stack
- Language: Python 3.11+
- Engine: PySpark 3.5+ (open-source) or Databricks Runtime 14+
- Storage: Delta Lake (ACID transactions, schema evolution, time travel)
- Experiment Tracking: MLflow (if pipeline produces a model)
- Testing: chispa (DataFrame equality), pytest
- Linting: ruff, mypy (--strict for job entrypoints)
- Orchestration: Databricks Workflows or Apache Airflow

## Architecture Shape
Data Pipeline — distributed data transformations using PySpark.
Use for: large-scale ETL/ELT, feature engineering at scale, batch data processing.
Use python-datascience for: exploratory analysis, model prototyping, notebook-first work.
Use python-dbt-snowflake for: SQL-first transformation logic, analytics engineering.

## Vibe & Style
- Coding Style: snake_case. Type hints on all functions. SparkSession injected, never created inside functions.
- Architecture: Medallion (Bronze → Silver → Gold). Each layer is a separate job or notebook.
- Pattern: Job entrypoint → transform functions → Delta write. No business logic in entrypoints.

## Key Rules
- SparkSession is injected — never call `SparkSession.builder` inside a transform function.
- All DataFrames are typed with StructType or use schema inference only at Bronze (raw) layer.
- Use Delta Lake for all persistent storage — no Parquet-only outputs.
- Test transform logic with chispa — do not test Spark infrastructure.
- Never collect() large DataFrames in production code.

## Active Phase
- Current: Phase 0 (Skeleton)
```

### `rules/000-spark-workflow.mdc`

- **Medallion-first**: define Bronze/Silver/Gold layers before writing transforms. Each layer has explicit schema.
- **Local-first development**: develop and test with small datasets locally (SparkSession with `master("local[2]")`). No cluster required for unit tests.
- **chispa test loop**: write failing chispa test → implement transform → green. Do not submit to cluster to verify logic.
- **CI gate**: `ruff check` → `mypy` → `pytest` → integration test on sample data. All pass before PR merge.
- **Delta commit messages**: use `COMMENT` in Delta operations to describe what each write does. Enables audit trail.

### `rules/100-spark-architecture.mdc`

- **Medallion layers**:
  - **Bronze**: raw ingestion. No transformations. Schema-on-read or inferred. Append-only. Keep source data forever.
  - **Silver**: cleaned, typed, deduplicated. Explicit StructType schema. SCD Type 2 for slowly-changing dimensions.
  - **Gold**: aggregated, business-ready. Optimized for consumption. Partitioned by query pattern.
- **SparkSession injection**: transform functions take `spark: SparkSession` as first argument. Never create SparkSession inside a function. Makes functions testable.
- **No collect() in production**: `collect()`, `toPandas()`, `show()` in production code are bugs. Use `.count()` for size checks. Write to Delta, not to Python variables.
- **Schema enforcement**: Silver and Gold layers use `mergeSchema=False` (reject unexpected columns). Bronze uses `mergeSchema=True` (tolerate upstream changes).
- **Partition strategy**: partition Gold tables by the most common filter column (date, region, category). Over-partitioning small tables is worse than under-partitioning.
- **Delta operations**: prefer `MERGE INTO` for upserts over overwrite. Use `OPTIMIZE` + `ZORDER BY` on query columns after large loads.
- **Job entrypoints**: `jobs/` directory. Each file is a standalone job. `if __name__ == "__main__"` creates SparkSession and calls orchestration function. No business logic in entrypoints.

### `rules/200-spark-testing.mdc`

- **chispa for DataFrame equality**: `from chispa import assert_df_equality`. Compares schema + data. Use `ignore_nullable=True` for schema comparison.
- **Spark test sessions**: conftest.py creates a `SparkSession` fixture with `master("local[2]")` and `enableHiveSupport=False`. Reuse across test file.
- **Test transform functions, not Spark**: do not test that Spark reads/writes work. Test that your transform logic produces the correct output DataFrame given an input.
- **Input fixtures as DataFrames**: create test inputs with `spark.createDataFrame(data, schema)`. Keep fixtures small (< 20 rows). Do not read from files in unit tests.
- **Integration tests with sample data**: maintain a `tests/fixtures/` directory with small Delta tables or CSV samples. Integration tests run against these. Tag with `@pytest.mark.integration`.
- **No cluster in CI**: unit tests run locally. Integration tests may run against Databricks or a local Spark. Never require a production cluster for CI.

### `rules/300-spark-style.mdc`

- **Type hints on all transform functions**: `def transform_sales(spark: SparkSession, df: DataFrame) -> DataFrame:`. Return type must be `DataFrame` or `Dataset`.
- **No `*` imports from pyspark**: `from pyspark.sql import functions as F`. Reference as `F.col()`, `F.lit()`, `F.when()`. Never `from pyspark.sql.functions import *`.
- **Column selection over select(\*)**: never `df.select("*")`. Always explicit column list or `df.columns` manipulation.
- **Descriptive column names in transforms**: if you alias a column, give it a business-meaningful name. `F.sum("revenue").alias("total_revenue")` not `F.sum("revenue").alias("sum1")`.
- **No hardcoded paths**: job configs use YAML or environment variables for source/destination paths. No `s3://my-bucket/path` in code.
- **Logging over print**: use Python `logging` module. Log row counts at each layer boundary: `logger.info("Silver write: %d rows", df.count())`.

### `templates/spark-starter.md`

Scaffold for a new Spark pipeline:
```
{pipeline-name}/
  jobs/
    ingest.py           (Bronze: read source → write raw Delta)
    transform.py        (Silver: clean + type → write typed Delta)
    aggregate.py        (Gold: aggregate → write business table)
  tests/
    conftest.py         (SparkSession fixture)
    test_transform.py   (chispa assertions on transform logic)
    test_aggregate.py
    fixtures/
      sample_raw.csv    (small test input)
  configs/
    job.yml             (source paths, destination paths, options)
  requirements.txt      (pyspark, delta-spark, chispa, mlflow, ruff, mypy, pytest)
```

Show example `conftest.py`:
```python
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("test")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )
```

Show example transform function signature:
```python
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

def clean_sales(spark: SparkSession, raw: DataFrame) -> DataFrame:
    return (
        raw
        .filter(F.col("amount").isNotNull())
        .withColumn("amount", F.col("amount").cast("double"))
        .withColumn("date", F.to_date(F.col("date_str"), "yyyy-MM-dd"))
        .drop("date_str")
    )
```

### `templates/job-config.yml`

```yaml
job:
  name: "{pipeline-name}-{layer}"
  description: "{what this job does}"

source:
  path: "s3://{bucket}/raw/{dataset}/"
  format: "delta"  # or csv, parquet, json

destination:
  path: "s3://{bucket}/{layer}/{dataset}/"
  format: "delta"
  mode: "merge"  # append, overwrite, merge

options:
  partition_by: ["date"]
  zorder_by: ["id"]
  merge_key: ["id", "date"]
```

### `templates/phase-checklist.md`

**Phase 0 — Skeleton:**
- [ ] Medallion layers defined (Bronze/Silver/Gold paths in config)
- [ ] Job entrypoints created (`jobs/ingest.py`, `jobs/transform.py`)
- [ ] SparkSession fixture in `conftest.py`
- [ ] `pytest` passes (no tests yet, but imports work)
- [ ] `ruff check` passes on empty skeleton

**Phase 1 — Bronze:**
- [ ] Ingest job reads source → writes raw Delta
- [ ] Schema documented (even if inferred)
- [ ] `chispa` test: ingest produces expected columns
- [ ] Integration test: small sample file → Delta write succeeds

**Phase 2+ — Silver/Gold:**
- [ ] Explicit StructType schema on Silver output
- [ ] `mergeSchema=False` on Silver/Gold writes
- [ ] All transform functions have type hints
- [ ] No `collect()` in production code
- [ ] `F.*` imports (no wildcard)

**Handoff:**
- [ ] `pytest` all green (unit + integration)
- [ ] `mypy --strict` on job entrypoints
- [ ] `OPTIMIZE` + `ZORDER` documented for each Gold table
- [ ] Row count logged at each layer boundary
- [ ] No hardcoded paths in code

### `vibe/vibe_architecture.md`

- **When Spark over pandas**: when data > RAM (typically > 10GB per partition), when you need distributed shuffle, when you need Delta ACID semantics on writes, or when the pipeline runs on a schedule in Databricks/EMR. For data < 1GB that fits in memory, use pandas — Spark adds complexity without benefit.
- **Medallion vs Star Schema**: Medallion (Bronze/Silver/Gold) is the operational pipeline structure — how data flows through quality layers. Star Schema (facts + dimensions) is the Gold layer's internal design — how business analysts query it. They are not alternatives; Gold is often a Star Schema.
- **Spark vs dbt**: Spark executes Python + SQL transformations on a distributed engine. dbt compiles SQL and runs it on a warehouse engine (Snowflake, BigQuery). Use Spark for Python-heavy transforms, ML feature engineering, streaming. Use dbt for SQL-first analytics modeling with lineage and testing.
- **Delta Lake vs Parquet**: Delta adds ACID transactions, schema enforcement, time travel, and DML (UPDATE/DELETE/MERGE) on top of Parquet files. Always use Delta for tables you write to more than once. Raw Parquet is acceptable for immutable Bronze archives.
- **Structured Streaming vs batch**: use Structured Streaming for sub-minute latency requirements. For hourly/daily pipelines, batch (Databricks Workflows trigger) is simpler. Streaming adds statefulness complexity.
- **PySpark vs Scala Spark**: Python is the default choice. Scala has better type safety and performance for complex UDFs, but Python + vectorized UDFs (pandas_udf) close most of the gap. Use Scala only when Python performance is demonstrably insufficient.

### `vibe/vibe_development_lifecycle.md`

References `stacks/shared/`. Adds Spark-specific:
- Local development with `local[2]` master — all unit tests run without cluster
- Sample data fixtures — maintain small test Delta tables checked into `tests/fixtures/`
- Databricks job submission — `databricks runs submit` or Databricks Workflows YAML for CI/CD
- Delta maintenance schedule — `OPTIMIZE` weekly, `VACUUM` (7-day retention minimum) monthly

### `examples/sales-pipeline/`

Five files — a complete Bronze→Silver pipeline:
- `jobs/ingest.py` — reads CSV from configured path, writes raw Delta to Bronze
- `jobs/transform.py` — reads Bronze Delta, casts types, filters nulls, writes to Silver with explicit schema
- `tests/conftest.py` — SparkSession fixture with Delta extensions
- `tests/test_transform.py` — chispa assertions: clean_sales removes nulls, casts amount to double, parses date
- `configs/job.yml` — source/destination paths, partition config

---

## Acceptance Criteria

- [ ] `ls stacks/python-spark/rules/` shows 4 files
- [ ] `ls stacks/python-spark/templates/` shows `spark-starter.md`, `phase-checklist.md`, `job-config.yml`
- [ ] `ls stacks/python-spark/vibe/` shows 2 docs
- [ ] `ls stacks/python-spark/examples/sales-pipeline/` shows jobs/, tests/, configs/
- [ ] `context.md` Architecture Shape = "Data Pipeline"
- [ ] `rules/100-spark-architecture.mdc` contains "No collect() in production" rule
- [ ] `rules/200-spark-testing.mdc` contains "chispa" testing pattern
- [ ] `vibe_architecture.md` contains "When Spark over pandas" decision section
