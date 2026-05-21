---
name: experiment-tracker
description: Logs experiment params, metrics, and artifacts
model: inherit
readonly: false
---

# Experiment Tracker Agent

Append a structured entry to `docs/experiments/log.md` for the current experiment run.

## Steps

1. **Read experiment context** — Extract the following from the current session context or from the experiment doc passed by `/ds-experiment`:
   - Experiment name
   - Timestamp (ISO 8601, UTC)
   - Seed value
   - Model type and key hyperparameters (condensed to fit a table cell)
   - Feature count and feature names (abbreviated if more than 10)
   - Target column
   - Train metrics (primary metric value)
   - Validation metrics (primary metric value)
   - Artifact paths (model file, any plots)
   - Notes (hypothesis tested, next experiment planned)

2. **Open or create `docs/experiments/log.md`** — If the file does not exist, create it with the header row. If it exists, append to the existing table.

3. **Append a table row** — The log uses a markdown table with one row per experiment run:

   ```markdown
   | Timestamp | Name | Seed | Model | Features | Train Metric | Val Metric | Artifacts | Notes |
   |---|---|---|---|---|---|---|---|---|
   | 2024-01-15T14:32Z | baseline-lr | 42 | LogisticRegression(C=1.0) | 12 features | acc=0.84 | acc=0.81 | artifacts/lr-baseline.pkl | Tests H1: age predicts churn |
   ```

4. **Report** — Confirm the entry was appended and return the path to `docs/experiments/log.md`.

## Log Format Rules

- One row per experiment run — never overwrite a previous row.
- Metric values include the metric name (e.g., `acc=0.84`, `rmse=2.31`, `f1=0.77`).
- Artifact paths are relative to the project root.
- Timestamps are UTC ISO 8601 (e.g., `2024-01-15T14:32Z`).
- The table must remain comparable across runs — use the same metric name and format each time.

## Notes

- This agent writes to `docs/experiments/log.md` and is therefore NOT readonly.
- If `docs/experiments/` does not exist, create it before writing.
- Do not edit or delete existing rows — only append.
