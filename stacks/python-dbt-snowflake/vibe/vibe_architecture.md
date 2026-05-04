# Architecture Vibe: Python dbt + Snowflake

## When dbt Over Spark

dbt wins when:
- The transformation logic is SQL — no Python custom UDFs, no pandas, no sklearn needed.
- The warehouse (Snowflake, BigQuery, Redshift) does the heavy lifting — you're paying for compute anyway; use it.
- Your team includes SQL-fluent analysts who should own the models — dbt democratizes transformation ownership.
- You need software engineering practices in your data layer: version control, tests, CI/CD, documentation, lineage.
- Your data volumes fit in a cloud warehouse (terabytes, not petabytes of daily processing).

Spark wins when:
- Transforms need Python: ML feature engineering, custom parsing, NLP, image processing.
- Data volume exceeds what a warehouse can handle efficiently (petabyte-scale raw processing).
- You need streaming or near-real-time transforms (use Spark Structured Streaming or Flink, not dbt).
- Your team is Python-first and SQL is a secondary concern.

Bottom line: if you're writing `SELECT ... FROM ... GROUP BY`, use dbt. If you're importing pandas, use Spark or a Python pipeline.

---

## Staging Is Sacred

The staging layer is the contract between your raw data and your models.

- Changing a staging model's column names or types is a **breaking change** — every downstream model that refs it may break.
- Never skip staging by referencing raw tables in marts directly. This couples your business logic to source system quirks. When the source system renames a column, you have to update every mart instead of just one staging model.
- Staging models absorb source system churn. Marts stay stable.
- Think of staging as the "clean room" — data enters dirty, exits standardized.

---

## dbt vs Stored Procedures

Stored procedures in Snowflake/BigQuery scatter transformation logic across the warehouse with no lineage, no testing, no version control. Common problems:
- "Where is this metric calculated?" — nobody knows, it's in three different stored procedures.
- "Why did this number change?" — no diff, no history, no tests to catch it.
- "Can we refactor this?" — terrifying, because nothing is tested.

dbt brings software engineering practices to SQL transformation:
- **Tests**: schema tests and custom data tests catch regressions.
- **Docs**: auto-generated lineage graph shows every dependency.
- **Version control**: every model change is a git commit with a diff and a code review.
- **CI/CD**: `dbt build` in CI catches broken models before they hit production.

The two are not equivalent. Stored procedures are imperative scripts. dbt models are declarative, testable, documented SQL.

---

## Incremental Model Strategy

Full refresh (`table` materialization) is always correct but expensive on large tables. Incremental is efficient but requires careful design.

Decision framework:
1. **Start with `table`** — simple, always correct, no edge cases. Acceptable for tables up to ~100M rows.
2. **Switch to `incremental` when build time becomes a problem** — not before. Premature optimization creates complexity.
3. **Incremental requirements**:
   - A reliable "updated at" column or event timestamp to filter new rows.
   - A `unique_key` to handle late-arriving data (rows that arrive after the incremental window).
   - Tested with `--full-refresh` to verify the full rebuild still works.
4. **Incremental edge cases** to handle:
   - Late-arriving data: rows for past periods that arrive after the incremental run.
   - Corrections/updates: source records that were updated after initial load.
   - Solution: use `unique_key` + `merge` strategy (Snowflake supports `MERGE`).

---

## dbt Metrics Layer

The dbt Semantic Layer (with MetricFlow) defines business metrics in YAML so BI tools query the same definition.

Why it matters: "Our revenue number is different in every report" is the most common complaint in analytics teams. It happens because Tableau, Looker, and the data warehouse each calculate revenue differently. The dbt Semantic Layer defines `revenue` once:

```yaml
metrics:
  - name: revenue
    label: Revenue
    type: simple
    type_params:
      measure: total_revenue_cents
    filter: "{{ Dimension('order__status') }} = 'completed'"
```

Every BI tool queries this definition. One source of truth.

Valuable when:
- Multiple BI tools (Tableau + Looker + custom SQL) query the same warehouse.
- Multiple teams (finance, product, marketing) report on the same metrics.
- Metric definitions drift between quarterly reviews and become a recurring source of confusion.

---

## dbt Cloud vs dbt Core

| | dbt Core | dbt Cloud |
|---|---|---|
| Cost | Free (open source) | Paid (per-seat or per-model) |
| Scheduling | External (Airflow, Dagster, cron) | Managed scheduler built-in |
| IDE | Local editor / CLI | Browser-based IDE |
| CI/CD | Configure yourself | Built-in PR checks |
| Semantic Layer | dbt Core + MetricFlow | Managed Semantic Layer |
| Best for | Teams with existing orchestration | Teams without DevOps capacity |

Use dbt Core when:
- You already have Airflow, Dagster, or Prefect for orchestration.
- Your team is comfortable with CLI tools and git-based workflows.
- You want to avoid per-seat SaaS pricing.

Use dbt Cloud when:
- You want a managed scheduler without maintaining Airflow.
- Your analysts prefer a browser IDE over a local development environment.
- You want built-in CI/CD without configuring GitHub Actions.
