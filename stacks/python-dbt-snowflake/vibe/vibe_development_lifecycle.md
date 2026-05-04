# Development Lifecycle Vibe: Python dbt + Snowflake

References `stacks/shared/` for general lifecycle patterns. This document adds dbt-specific practices.

---

## Personal Dev Schema

Each developer has their own Snowflake schema as their dbt target. No sharing the prod schema in development.

Convention: `dbt_{username}` (e.g., `dbt_axel`, `dbt_sarah`).

In `profiles.yml`:
```yaml
dev:
  schema: "dbt_{{ env_var('DBT_USER', target.user) }}"
```

Why this matters:
- Developer A's half-finished `fct_revenue` doesn't break Developer B's dashboard queries.
- You can run `dbt build` without fear of overwriting prod data.
- Easy cleanup: drop your personal schema to reset.

---

## Incremental CI with State

dbt tracks the state of the last successful run in `manifest.json`. Use this for fast CI:

```bash
# Only rebuild models that changed in this PR + their downstream dependencies
dbt build --select state:modified+
```

Setup:
1. Upload `manifest.json` as a CI artifact after each successful production run.
2. Download the production `manifest.json` at the start of each CI run.
3. Pass `--state ./prod-manifest/` to the `dbt build` command.

This makes CI fast even in large projects with hundreds of models — you only rebuild what changed.

---

## Branch-Based Deploys

One dbt Cloud job (or Airflow DAG) per environment:

| Branch | Environment | Trigger | Schema |
|---|---|---|---|
| `feature/*` | Developer dev | Manual / on push | `dbt_{username}` |
| `develop` | Staging | On PR merge to develop | `analytics_staging` |
| `main` | Production | On PR merge to main | `analytics` |

Rules:
- Staging deploys run `dbt build` on full project — catches issues before prod.
- Prod deploys use `dbt build --select state:modified+` for speed, plus `dbt source freshness` before transformations.
- Never deploy to prod by running dbt locally. All prod runs go through CI/CD.

---

## Documentation as a Deliverable

`dbt docs generate` + `dbt docs serve` is the handoff artifact when a project or phase is complete.

Column descriptions are required, not optional:
- A model without column descriptions is not done — it's a liability.
- Future analysts will query your model without knowing what columns mean.
- The lineage graph is only useful if every node has a description.

Documentation workflow:
```bash
# Generate docs + lineage graph
dbt docs generate

# Serve locally and review
dbt docs serve
# Open http://localhost:8080

# Check coverage: every model and column should have a description
# Use dbt_project_evaluator package to enforce documentation coverage
dbt run --select dbt_project_evaluator
```

Handoff checklist:
- [ ] `dbt docs generate` runs without errors
- [ ] Every model has a description with grain statement
- [ ] Every column has a meaningful description (not placeholder text)
- [ ] Lineage graph reviewed — no orphaned models, no unexpected dependencies

---

## Local Development Workflow

Day-to-day development loop:

```bash
# 1. Start from a fresh branch
git checkout -b feature/add-fct-revenue

# 2. Create the staging model + yml (if not exists)
# models/staging/stg_orders.sql + models/staging/_stg_orders.yml

# 3. Compile to check for syntax errors
dbt compile --select stg_orders

# 4. Run the model in your dev schema
dbt run --select stg_orders

# 5. Run tests
dbt test --select stg_orders

# 6. Build marts that depend on the staging model
dbt build --select fct_revenue+

# 7. Lint before committing
sqlfluff lint --dialect snowflake models/staging/stg_orders.sql

# 8. Commit and push
git add models/staging/stg_orders.sql models/staging/_stg_orders.yml
git commit -m "feat: add stg_orders staging model"
git push
```

---

## Debugging Common Issues

**`dbt run` fails with "relation does not exist"**
- Source table not found: check `_sources.yml` database/schema/table names match actual Snowflake objects.
- Wrong target: you may be pointing at dev schema but the source is only in prod. Check `profiles.yml`.

**`dbt test` fails with "unique" test**
- Duplicates in your source data. Add deduplication in the staging model using `ROW_NUMBER()` or `QUALIFY`.
- Check if `unique_key` is correctly defined for incremental models.

**`sqlfluff lint` fails**
- Most common: missing trailing comma, inconsistent indentation, lowercase SQL keyword.
- Run `sqlfluff fix --dialect snowflake models/path/to/model.sql` for auto-fix on safe rules.

**Incremental model has stale/missing data**
- The `is_incremental()` filter may be excluding rows it shouldn't.
- Run with `--full-refresh` to rebuild from scratch: `dbt run --select fct_revenue --full-refresh`.
- Check the `updated_at` field is actually being updated in the source system.
