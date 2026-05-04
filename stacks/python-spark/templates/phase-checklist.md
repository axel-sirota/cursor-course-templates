# Phase Checklist: Python Spark Pipeline

Use this checklist to track progress through each development phase.

---

## Phase 0 — Skeleton

- [ ] Medallion layers defined (Bronze/Silver/Gold paths in config)
- [ ] Job entrypoints created (`jobs/ingest.py`, `jobs/transform.py`)
- [ ] SparkSession fixture in `conftest.py`
- [ ] `pytest` passes (no tests yet, but imports work)
- [ ] `ruff check` passes on empty skeleton

---

## Phase 1 — Bronze

- [ ] Ingest job reads source → writes raw Delta
- [ ] Schema documented (even if inferred)
- [ ] `chispa` test: ingest produces expected columns
- [ ] Integration test: small sample file → Delta write succeeds

---

## Phase 2 — Silver

- [ ] Explicit StructType schema on Silver output
- [ ] `mergeSchema=False` on Silver writes
- [ ] All transform functions have type hints
- [ ] No `collect()` in production code
- [ ] `F.*` imports (no wildcard)
- [ ] Null handling documented and tested
- [ ] Deduplication logic tested with chispa

---

## Phase 3 — Gold

- [ ] Aggregations are tested with chispa
- [ ] Partition strategy documented in `configs/job.yml`
- [ ] `mergeSchema=False` on Gold writes
- [ ] No hardcoded paths in any job file
- [ ] Row counts logged at Gold write

---

## Handoff

- [ ] `pytest` all green (unit + integration)
- [ ] `mypy --strict` on job entrypoints passes
- [ ] `ruff check` passes with zero warnings
- [ ] `OPTIMIZE` + `ZORDER` documented for each Gold table
- [ ] Row count logged at each layer boundary
- [ ] No hardcoded paths in code
- [ ] `VACUUM` schedule documented in runbook
- [ ] Delta schema for Silver and Gold committed to repo
- [ ] CI pipeline runs `ruff` → `mypy` → `pytest` in order
