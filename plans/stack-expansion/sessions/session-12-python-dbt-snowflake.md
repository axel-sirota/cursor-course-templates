# Session 12 — New Stack: `python-dbt-snowflake`

**Phase:** 3 — Group C (data-scientist persona)
**Parallel with:** Sessions 7, 8, 9, 10, 11
**Depends on:** Sessions 1–6 complete
**Client fit:** Analytics engineering teams, data teams on Snowflake/BigQuery, anyone doing SQL-first transformation

## Architecture Shape
Analytics Model — dbt Core models transforming raw warehouse data into analytics-ready tables. SQL-first. Snowflake (or BigQuery) as the execution engine. Not a web API. Not a pipeline (use python-spark for Python-heavy transforms).

---

## Files to Create

```
stacks/python-dbt-snowflake/
├── context.md
├── rules/
│   ├── 000-dbt-workflow.mdc
│   ├── 100-dbt-architecture.mdc
│   ├── 200-dbt-testing.mdc
│   └── 300-dbt-style.mdc
├── templates/
│   ├── dbt-starter.md
│   ├── phase-checklist.md
│   └── schema.yml
├── vibe/
│   ├── vibe_architecture.md
│   └── vibe_development_lifecycle.md
└── examples/
    └── revenue-models/
        ├── models/
        │   ├── staging/
        │   │   ├── stg_orders.sql
        │   │   └── _stg_orders.yml
        │   └── marts/
        │       ├── fct_revenue.sql
        │       └── _fct_revenue.yml
        ├── tests/
        │   └── assert_revenue_positive.sql
        └── dbt_project.yml
```

---

## File Specifications

### `context.md`

```markdown
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
```

### `rules/000-dbt-workflow.mdc`

- **Model-first**: create the `.sql` file and its `.yml` description file together. Never a model without a yml.
- **Staging before marts**: build staging models first. No mart can exist without its source staging models.
- **`dbt run` + `dbt test` loop**: after each model change, run `dbt run -s model_name` then `dbt test -s model_name`. Both must pass.
- **CI gate**: `sqlfluff lint` → `dbt compile` → `dbt run` → `dbt test` → `dbt docs generate`. All pass on PR.
- **No `dbt run` on prod without `--target prod`**: always explicit about target. Default profile target is `dev` (your personal Snowflake schema).

### `rules/100-dbt-architecture.mdc`

- **Layer responsibilities**:
  - **Staging (`stg_*`)**: 1:1 with source tables. Rename columns to snake_case. Cast types. No joins. No aggregations.
  - **Intermediate (`int_*`)**: optional. Complex multi-source joins, pivots, business logic that is reused. Not exposed to BI.
  - **Marts (`fct_*`, `dim_*`)**: business-ready. Aggregated facts, conformed dimensions. Exposed to BI tools.
- **`{{ source() }}` in staging only**: staging models reference `{{ source('raw_schema', 'table') }}`. All other models use `{{ ref() }}`. Enforced by dbt-checkpoint.
- **`{{ ref() }}` everywhere else**: never hardcode `database.schema.table` in a model. `{{ ref('stg_orders') }}` compiles to the correct target schema automatically.
- **Incremental models**: use `{{ config(materialized='incremental') }}` for large fact tables. Always include `is_incremental()` guard. Define `unique_key` to handle late-arriving data.
- **Materializations**:
  - `view`: staging models (cheap, always fresh).
  - `table`: marts (fast for BI, refreshed on each run).
  - `incremental`: large fact tables that grow daily.
  - `ephemeral`: intermediate CTEs that don't need their own table.
- **Macros for reuse**: extract repeated SQL patterns into `macros/`. Use `{{ macro_name(args) }}` in models. Don't copy-paste SQL across models.
- **Packages**: use `dbt_utils` (codegen, pivot, surrogate_key). Pin versions in `packages.yml`. Run `dbt deps` after updating.

### `rules/200-dbt-testing.mdc`

- **Every model has tests**: at minimum `not_null` + `unique` on the primary key in the `.yml` file. No exceptions.
- **Built-in test types**: `not_null`, `unique`, `accepted_values`, `relationships`. Use all four where appropriate before writing custom SQL tests.
- **Custom data tests** (`tests/` directory): SQL files that return rows when the test FAILS. Used for business logic assertions: `assert_revenue_positive.sql` returns rows where `revenue < 0`.
- **`dbt test --select` in development**: run tests on the current model only during development. Run full `dbt test` on CI.
- **`dbt build` in CI**: use `dbt build` (runs + tests together in DAG order) instead of separate `dbt run` then `dbt test`. Fails fast on first bad model.
- **Source freshness**: define `freshness` in `sources.yml` for all sources. `dbt source freshness` in CI catches stale data before transformations run.
- **Elementary or re_data for observability**: add table-level anomaly detection for row count drops and null rate spikes on production marts.

### `rules/300-dbt-style.mdc`

- **CTE-first**: every model is structured as a series of named CTEs, not nested subqueries. Final SELECT is clean.
  ```sql
  with source as (select * from {{ source(...) }}),
  renamed as (select id, created_at::date as order_date from source),
  final as (select * from renamed)
  select * from final
  ```
- **snake_case everywhere**: model names, column names, CTE names, macro names. No camelCase, no PascalCase.
- **Column naming conventions**:
  - Primary keys: `{model_name}_id` (e.g., `order_id`)
  - Foreign keys: `{referenced_model}_id` (e.g., `customer_id`)
  - Booleans: `is_*` or `has_*` prefix (e.g., `is_deleted`, `has_discount`)
  - Dates: `*_at` for timestamps, `*_date` for dates
- **No SELECT ***: always explicit column list in final SELECT. `SELECT *` acceptable only in `source` CTE at the top of staging model.
- **sqlfluff**: run `sqlfluff lint --dialect snowflake` before commit. Use `.sqlfluff` config in project root. Enforce: uppercase SQL keywords, trailing comma style, max line length 120.
- **`.yml` descriptions**: every column in `.yml` has a non-empty `description`. "The order ID" is not a description. Describe what it means: "Unique identifier for a placed order, sourced from the orders table in the transactional database."

### `templates/dbt-starter.md`

Scaffold for a new dbt project:
```
{project-name}/
  dbt_project.yml         (project name, profile, model configs by directory)
  profiles.yml            (connection — dev schema = personal, prod schema = analytics)
  packages.yml            (dbt-utils, dbt-expectations, dbt-checkpoint)
  .sqlfluff               (dialect: snowflake, rules config)
  models/
    staging/
      _sources.yml        ({{ source() }} definitions for all raw tables)
      stg_{source}_{table}.sql
      _stg_{source}_{table}.yml
    intermediate/         (optional)
      int_{name}.sql
      _int_{name}.yml
    marts/
      fct_{name}.sql
      _fct_{name}.yml
      dim_{name}.sql
      _dim_{name}.yml
  tests/
    assert_{condition}.sql
  macros/
    {utility_name}.sql
  seeds/
    {lookup_table}.csv    (small static reference data)
```

Show example `_sources.yml`:
```yaml
version: 2
sources:
  - name: raw_ecommerce
    database: raw
    schema: ecommerce
    freshness:
      warn_after: {count: 24, period: hour}
      error_after: {count: 48, period: hour}
    loaded_at_field: _loaded_at
    tables:
      - name: orders
        description: "Raw orders from the transactional database."
```

Show example staging model `.yml`:
```yaml
version: 2
models:
  - name: stg_orders
    description: "Staged orders, 1:1 with raw.ecommerce.orders. Renamed and typed."
    columns:
      - name: order_id
        description: "Unique order identifier."
        tests:
          - not_null
          - unique
      - name: customer_id
        description: "Foreign key to stg_customers."
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id
```

### `templates/schema.yml`

```yaml
version: 2

models:
  - name: {model_name}
    description: "{what this model represents and its grain}"
    config:
      materialized: {view|table|incremental}
    columns:
      - name: {primary_key}_id
        description: "{description}"
        tests:
          - not_null
          - unique
      - name: {foreign_key}_id
        description: "{description}"
        tests:
          - not_null
          - relationships:
              to: ref('{referenced_model}')
              field: {foreign_key}_id
      - name: {date_column}_at
        description: "{description}"
        tests:
          - not_null
```

### `templates/phase-checklist.md`

**Phase 0 — Skeleton:**
- [ ] `dbt_project.yml` configured with correct profile and model directories
- [ ] `_sources.yml` defines all raw source tables
- [ ] Staging model stubs created (return `select 1 as placeholder`)
- [ ] `dbt compile` succeeds
- [ ] All staging `.yml` files created (even if descriptions are TODO)

**Phase 1 — Staging:**
- [ ] All staging models complete (rename, cast, no joins)
- [ ] `not_null` + `unique` tests on all primary keys
- [ ] `dbt test -s staging` all green
- [ ] `sqlfluff lint` passes on all staging models
- [ ] Source freshness configured

**Phase 2+ — Marts:**
- [ ] `fct_*` and `dim_*` models built on top of staging/intermediate
- [ ] Incremental materializations for large fact tables
- [ ] Relationships tests between facts and dimensions
- [ ] Column descriptions complete in all `.yml` files
- [ ] No hardcoded schema names (all `{{ ref() }}`)

**Handoff:**
- [ ] `dbt build` full pass (run + test in DAG order)
- [ ] `dbt docs generate` — lineage graph complete, all models documented
- [ ] `dbt source freshness` passes
- [ ] `sqlfluff lint --dialect snowflake` zero errors
- [ ] Custom data tests cover business-critical assertions

### `vibe/vibe_architecture.md`

- **When dbt over Spark**: dbt wins when the transformation logic is SQL (no Python needed), when the warehouse (Snowflake, BigQuery, Redshift) does the heavy lifting, and when your team includes SQL-fluent analysts who should own the models. Spark wins when transforms need Python (ML features, custom UDFs), when data volume exceeds what a warehouse can handle efficiently, or when you need streaming.
- **Staging is sacred**: the staging layer is the contract between your raw data and your models. Changing a staging model's column names or types is a breaking change. Never skip staging by referencing raw tables in marts directly — this couples your business logic to source system quirks.
- **dbt vs stored procedures**: stored procedures in Snowflake/BigQuery scatter transformation logic across the warehouse with no lineage, no testing, no version control. dbt brings software engineering practices (tests, docs, CI/CD, version control) to SQL transformation. The two are not equivalent.
- **Incremental model strategy**: full refresh (`table`) is always correct but expensive on large tables. Incremental is efficient but requires a correct `unique_key` and `is_incremental()` guard. Start with `table` (simple, correct), switch to `incremental` only when build time becomes a problem.
- **dbt metrics layer**: dbt Semantic Layer (with MetricFlow) defines business metrics in YAML so BI tools query the same definition. Avoids metric divergence between dashboards ("our revenue number is different in every report"). Valuable when multiple BI tools or teams share the same warehouse.
- **dbt Cloud vs dbt Core**: dbt Core is the open-source CLI. dbt Cloud adds a managed scheduler, IDE, CI/CD integration, and the Semantic Layer. Use Core for teams with existing orchestration (Airflow, Dagster). Use Cloud for teams without DevOps capacity or wanting managed scheduling.

### `vibe/vibe_development_lifecycle.md`

References `stacks/shared/`. Adds dbt-specific:
- Personal dev schema: each developer has their own Snowflake schema as dbt target — `dev_{username}`. No sharing prod schema in development.
- `dbt build --select state:modified+` — incremental CI: only rebuild models changed in this PR and their downstream dependencies.
- Branch-based deploys: one dbt Cloud job per environment. Dev deploys on branch push. Staging deploys on PR merge to develop. Prod deploys on merge to main.
- Documentation as a deliverable: `dbt docs generate` + `dbt docs serve` is the handoff artifact. Column descriptions are required, not optional.

### `examples/revenue-models/`

Seven files — a complete staging → marts pipeline:
- `dbt_project.yml` — project config, model materializations by directory
- `models/staging/stg_orders.sql` — staging model: rename columns, cast types, no joins
- `models/staging/_stg_orders.yml` — schema: description, not_null + unique on order_id, relationships test on customer_id
- `models/marts/fct_revenue.sql` — incremental fact table: daily revenue aggregation from stg_orders + stg_order_items
- `models/marts/_fct_revenue.yml` — schema: grain documented, not_null on all key columns, accepted_values test
- `tests/assert_revenue_positive.sql` — custom test: returns rows where daily_revenue < 0 (should return 0 rows)

---

## Acceptance Criteria

- [ ] `ls stacks/python-dbt-snowflake/rules/` shows 4 files
- [ ] `ls stacks/python-dbt-snowflake/templates/` shows `dbt-starter.md`, `phase-checklist.md`, `schema.yml`
- [ ] `ls stacks/python-dbt-snowflake/vibe/` shows 2 docs
- [ ] `ls stacks/python-dbt-snowflake/examples/revenue-models/` shows dbt_project.yml + models/ + tests/
- [ ] `context.md` Architecture Shape = "Analytics Model"
- [ ] `rules/000-dbt-workflow.mdc` contains "`{{ source() }}` in staging only" rule
- [ ] `rules/200-dbt-testing.mdc` contains "Every model has tests" rule
- [ ] `vibe_architecture.md` contains "When dbt over Spark" decision section
