# Project Context: Python dbt + Snowflake

## Tech Stack
- Transformation: dbt Core 1.8+ (or dbt Cloud)
- Warehouse: Snowflake (primary) or BigQuery (supported)
- Language: SQL (Jinja2 templating via dbt macros)
- Testing: dbt tests (built-in: not_null, unique, accepted_values, relationships) + custom SQL tests
- Linting: sqlfluff (dbt dialect), dbt-checkpoint (pre-commit hooks)
- Docs: dbt docs generate (auto-generated lineage + column docs)
- Orchestration: dbt Cloud, Airflow (BashOperator / dbt-airflow), or Dagster

## Architecture Shape
Analytics Model — SQL-first data modeling on a cloud warehouse.
Use for: analytics engineering, BI layer, metric definitions, business logic in SQL.
Use python-spark for: Python-heavy transforms, ML feature pipelines, streaming data.
Use python-datascience for: exploratory analysis, model prototyping, notebooks.

## Vibe & Style
- Coding Style: snake_case for all models, sources, columns. CTEs over nested subqueries.
- Architecture: Staging → Intermediate (optional) → Marts. One model per file. Refs not hardcoded schema names.
- Pattern: `{{ source() }}` in staging only. `{{ ref() }}` everywhere else. No direct table references.

## Key Rules
- Never reference raw tables directly — always `{{ source('schema', 'table') }}` in staging models.
- All inter-model references use `{{ ref('model_name') }}` — never hardcoded schema.table.
- Every model has a `.yml` file with at minimum: description, column descriptions, not_null + unique tests on primary key.
- Staging models are 1:1 with source tables — no joins, no aggregations. Just renaming, casting, light cleaning.
- Marts are business-facing — fact tables (fct_*), dimension tables (dim_*). Marts may join staging/intermediate models.

## Active Phase
- Current: Phase 0 (Skeleton)
