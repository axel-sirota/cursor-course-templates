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
