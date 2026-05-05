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

## Entry Point & Structure
- **Entry point**: `dbt_project.yml` — defines the project name, profile, and model directory config; the first file `dbt run` reads
- **Model entry**: `models/staging/` → `models/intermediate/` (optional) → `models/marts/` — models run in DAG order, not sequentially
- **Source definitions**: `models/staging/_sources.yml` — all raw table references via `{{ source() }}` live here
- **Directory layout**:
  ```
  models/
    staging/         ← 1:1 with raw sources; views; {{ source() }} only here
    intermediate/    ← optional; complex joins/pivots; {{ ref() }} only
    marts/           ← business-facing; fct_* and dim_*; {{ ref() }} only
  tests/             ← custom data tests (SQL files returning failing rows)
  macros/            ← reusable Jinja2 SQL macros
  seeds/             ← small static CSV lookup tables
  analyses/          ← ad-hoc SQL (not part of the DAG)
  ```
- **Config/env**: `profiles.yml` (outside project dir, usually `~/.dbt/profiles.yml`) for warehouse connection; env vars via `{{ env_var('VAR_NAME') }}` in profiles.yml
- **No application persistence**: dbt transforms data inside the warehouse — there is no application database to scaffold. The warehouse IS the persistence layer.
- **Test command**: `dbt test` (all tests) or `dbt build` (run + test in DAG order, preferred in CI)

## Active Phase
- Current: Phase 0 (Skeleton)
