# Vibe Guide: Data Science Workflow

## Overview

Data science work follows a four-phase pipeline:

```
Explore (EDA) → Experiment → Validate → Handoff
       ↑               |
       └───────────────┘  (iterate back when results are weak)
```

Each phase has a clear entry condition, deliverables, and exit condition. Do not skip phases. Do not model before you have explored.

---

## Why EDA Comes Before Modeling

The most common DS mistake is rushing to a model before understanding the data. This wastes experiment compute, produces misleading results, and generates undiagnosed data quality bugs.

EDA answers:
- Are there null values, outliers, or impossible values?
- Is the target variable skewed or imbalanced?
- Are features correlated with the target, or with each other?
- Is there potential label leakage (a feature that contains the target)?
- Do train and test distributions match?

If you skip EDA, you will discover these problems during Experiment — after spending time training a model that was doomed from the start.

**Rule**: No model code until you can answer all five questions above.

---

## Phase 1: Explore (EDA)

**Entry condition**: Raw data is available (path + checksum documented).

**Activities**:
- Load data, print shape and dtypes
- Compute null counts and null rates per column
- Plot target distribution
- Plot feature distributions and flag skew / outliers
- Compute correlation matrix
- Write your hypothesis (Section 4 of ds-starter template)

**Deliverable**: A notebook (`01-eda.ipynb`) with findings documented in markdown cells and a written hypothesis section.

**Exit condition**: You can describe in plain language what the data contains, what you expect to predict, and what baseline to beat.

---

## Phase 2: Experiment

**Entry condition**: EDA complete and hypothesis written.

**Activities**:
- Define feature set based on EDA findings
- Set seed (mandatory — see `000-ds-workflow.mdc`)
- Train one or more model variants
- Log every run: params, metrics, seed, artifact paths
- Compare runs against the naive baseline

**Deliverable**: A notebook (`02-experiment.ipynb`) with logged runs and a clear best-run selected.

**Exit condition**: At least one model beats the baseline on the primary metric. All runs are logged. Best model artifact is saved.

**When to iterate back to EDA**:
- Model performance is near baseline despite tuning → suspect data quality, feature engineering, or leakage
- Validation score is much worse than train score → check for leakage or distribution mismatch
- Results are inconsistent across seeds → investigate class imbalance or low-signal features

---

## Phase 3: Validate

**Entry condition**: A best-run model selected from Experiment phase.

**Activities**:
- Re-run the winning experiment on a held-out test set (used only once)
- Confirm metrics are consistent with validation performance
- Check for edge cases: rare classes, extreme values, missing inputs
- Run the notebook clean top-to-bottom (Restart + Run All)
- Confirm artifact paths are saved and reproducible

**Deliverable**: A notebook (`03-evaluation.ipynb`) with held-out test metrics, error analysis, and a passing clean run.

**Exit condition**: Test metrics are consistent with validation metrics. Notebook passes clean run. No data leakage or reproducibility issues found.

**When to iterate back to Experiment**:
- Test metrics are significantly worse than validation → possible overfitting or leakage
- Edge case analysis reveals a critical failure mode → fix features and retrain

---

## Phase 4: Handoff

**Entry condition**: Validate phase complete; model is production-worthy.

**Activities**:
- Write the model card (`reports/model_card.md`)
- Package reusable code into `src/` modules (feature engineering, predict function)
- Write a brief engineering handoff document (input/output schema, expected latency, dependencies)
- Confirm all artifacts are saved and paths are documented
- Final clean run check

**Deliverable**: `reports/model_card.md`, `src/` modules, handoff document, and all notebooks passing clean runs.

**Exit condition**: An engineer with no prior context can read the model card and handoff doc, find the saved model artifact, and integrate it without needing to talk to the DS team.

---

## What "Done" Looks Like

A DS task is complete when all of the following are true:

1. **Reproducibility**: Any team member can clone the repo, install requirements, and reproduce the final model by running notebooks in order on a fresh kernel.
2. **Model card written**: Describes training data, metrics, known limitations, and how to load/run the model.
3. **Clean notebook run**: All notebooks pass Restart + Run All with no errors.
4. **Experiment log**: Every training run is recorded with params, metrics, seed, and artifact path.
5. **No raw data in the repo**: `.gitignore` covers `data/raw/` and `data/processed/`; only paths and checksums are committed.
6. **Engineering handoff doc**: Input/output schema, dependencies, expected latency, and edge case behavior are documented.

If any of these are missing, the task is not done.

---

## Quick Reference: When to Iterate

| Symptom | Likely cause | Action |
|---|---|---|
| Model barely beats baseline | Weak features or wrong model class | Back to EDA: check feature engineering |
| Train >> Val score | Overfitting or leakage | Back to EDA: check for leakage; back to Experiment: add regularization |
| Val >> Test score | Distribution shift or data prep bug | Back to EDA: inspect test set distribution |
| Metrics vary across seeds | Instability from class imbalance or small data | Back to Experiment: stratify splits, adjust class weights |
| Clean run fails | Notebook state pollution | Fix cell order, remove out-of-order state dependencies |
