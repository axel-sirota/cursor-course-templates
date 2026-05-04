# dbt Project Phase Checklist

## Phase 0 — Skeleton

- [ ] `dbt_project.yml` configured with correct profile and model directories
- [ ] `profiles.yml` created with `dev` and `prod` targets (dev uses personal schema `dbt_{username}`)
- [ ] `packages.yml` lists `dbt_utils`, `dbt-expectations`, `dbt-checkpoint` with pinned versions
- [ ] `dbt deps` runs successfully — all packages installed
- [ ] `_sources.yml` defines all raw source tables with `database`, `schema`, and `freshness` config
- [ ] Staging model stubs created (return `select 1 as placeholder` or minimal select)
- [ ] `dbt compile` succeeds — no Jinja errors, all refs resolve
- [ ] All staging `.yml` files created (even if descriptions are TODO placeholders)
- [ ] `.sqlfluff` config committed to repo root
- [ ] `dbt debug` confirms warehouse connectivity in dev environment

---

## Phase 1 — Staging

- [ ] All staging models complete: rename columns to snake_case, cast types, no joins, no aggregations
- [ ] Every staging model is 1:1 with its source table — one model per source table
- [ ] `{{ source() }}` macro used in all staging models — no hardcoded table references
- [ ] `not_null` + `unique` tests on all primary keys
- [ ] `relationships` tests on all foreign keys that reference other staged models
- [ ] `accepted_values` tests on all status/enum columns
- [ ] `dbt test --select staging` — all green
- [ ] `sqlfluff lint` passes on all staging models — zero errors
- [ ] Source freshness configured with `loaded_at_field` for all time-stamped sources
- [ ] `dbt source freshness` runs without errors
- [ ] Column descriptions in staging `.yml` files are meaningful (not placeholder text)

---

## Phase 2 — Intermediate (if needed)

- [ ] Intermediate models identified: multi-source joins or logic reused by 2+ marts
- [ ] All intermediate models use `{{ ref() }}` — no `{{ source() }}`
- [ ] Intermediate models materialized as `ephemeral` or `view` (not `table`)
- [ ] Intermediate `.yml` files created with descriptions and tests
- [ ] `dbt build --select intermediate` passes
- [ ] No business-facing columns exposed directly from intermediate layer

---

## Phase 2+ — Marts

- [ ] `fct_*` and `dim_*` models built on top of staging/intermediate — no direct `{{ source() }}` references
- [ ] Grain documented in each mart's `.yml` description ("One row per order per day")
- [ ] Incremental materializations for large fact tables (`fct_*` with daily growth)
- [ ] `is_incremental()` guard implemented correctly in all incremental models
- [ ] `unique_key` defined in incremental model config for deduplication
- [ ] `relationships` tests between fact columns and dimension primary keys
- [ ] Column descriptions complete in all `.yml` files — no empty or placeholder descriptions
- [ ] No hardcoded schema names anywhere — all inter-model references use `{{ ref() }}`
- [ ] Custom data tests in `tests/` for critical business logic assertions
- [ ] `dbt build --select marts` passes

---

## Handoff / Production Readiness

- [ ] `dbt build` — full project run + test in DAG order, all green
- [ ] `dbt docs generate` — lineage graph complete, all models documented
- [ ] `dbt docs serve` — lineage graph reviewed, no orphaned models
- [ ] `dbt source freshness` passes — all sources within freshness thresholds
- [ ] `sqlfluff lint --dialect snowflake` — zero errors across entire `models/` directory
- [ ] Custom data tests cover all business-critical assertions
- [ ] Incremental models tested with `--full-refresh` flag to verify full rebuild works
- [ ] Prod target configured and tested with `dbt compile --target prod`
- [ ] CI/CD pipeline configured: `dbt build --select state:modified+` on PR, full `dbt build` on merge to main
- [ ] Observability (Elementary or re_data) configured for production mart anomaly detection
- [ ] `packages.yml` versions pinned and reviewed — no `*` wildcards
