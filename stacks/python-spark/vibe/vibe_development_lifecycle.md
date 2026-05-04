# Development Lifecycle Vibe: Python Spark

References `stacks/shared/` for general practices. This document covers Spark-specific lifecycle additions.

---

## Local Development with `local[2]`

All unit tests run without a cluster. The `SparkSession` fixture in `conftest.py` uses `master("local[2]")` — two local threads simulating a small cluster. This means:

- Any developer with PySpark installed can run the full unit test suite
- CI does not require Spark infrastructure
- Transform logic is verified before cluster submission
- Iteration speed is seconds, not minutes

Configure your local environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install pyspark delta-spark chispa pytest ruff mypy pyyaml
pytest tests/ -m "not integration"
```

---

## Sample Data Fixtures

Maintain small test data in `tests/fixtures/`. These are checked into git.

- CSV files for Bronze ingestion tests (< 50 rows)
- Small Delta tables for Silver/Gold integration tests (generate once, commit)
- Never use production data in fixtures

Fixture generation script pattern:
```python
# scripts/generate_fixtures.py
spark = SparkSession.builder.master("local[1]").getOrCreate()
sample = spark.createDataFrame([...], schema)
sample.write.format("delta").save("tests/fixtures/sample_bronze/")
```

---

## Databricks Job Submission

For CI/CD against a real cluster:

```bash
# Submit a one-time run
databricks runs submit --json '{
  "run_name": "sales-transform-ci",
  "new_cluster": {...},
  "python_task": {
    "python_file": "jobs/transform.py"
  }
}'
```

For production scheduling, use Databricks Workflows YAML:
```yaml
# .databricks/bundle.yml
resources:
  jobs:
    sales_transform:
      name: sales-transform
      tasks:
        - task_key: transform
          python_wheel_task:
            package_name: sales_pipeline
            entry_point: transform
```

---

## Delta Maintenance Schedule

Delta tables require periodic maintenance to stay performant.

### OPTIMIZE (Weekly)
Compacts small files into larger ones. Improves read performance.
```sql
OPTIMIZE delta.`s3://bucket/silver/sales/` ZORDER BY (id, date)
```

### VACUUM (Monthly, minimum 7-day retention)
Removes old file versions. Never set retention below 7 days — this breaks time-travel queries and concurrent readers.
```sql
VACUUM delta.`s3://bucket/silver/sales/` RETAIN 168 HOURS
```

### Log Retention
Delta transaction logs older than 30 days can be cleaned. Databricks handles this automatically if log retention is configured:
```python
spark.conf.set("spark.databricks.delta.logRetentionDuration", "interval 30 days")
```

---

## Layer Handoff Protocol

When a layer is complete, verify:
1. Row count logged at the write boundary
2. Schema committed to repo (Silver/Gold only)
3. `chispa` tests cover null handling, type casting, deduplication
4. Integration test runs against `tests/fixtures/` data
5. `ruff check` and `mypy --strict` pass on the job entrypoint
6. OPTIMIZE + ZORDER documented in `configs/job.yml`

---

## Performance Debugging Checklist

When a job is slow:
1. Check partition count — too few causes skew, too many causes small file overhead
2. Check for shuffle-heavy operations — joins on non-partitioned columns
3. Enable AQE (Adaptive Query Execution): `spark.conf.set("spark.sql.adaptive.enabled", "true")`
4. Profile with Spark UI — look for skewed stages (one task >> median)
5. Check Delta file sizes — run OPTIMIZE if many small files
6. Check broadcast threshold for small dimension tables: `spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50m")`
