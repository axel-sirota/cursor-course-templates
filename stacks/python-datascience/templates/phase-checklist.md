# Phase Checklist

Use this checklist to verify completion before moving to the next phase. Each phase must be fully checked before proceeding.

---

## Phase: Explore (EDA)

- [ ] Raw data added with DVC (`dvc add data/raw/`)
- [ ] `data/README.md` documents dataset (source, date, schema, rows, license)
- [ ] EDA notebook runs top-to-bottom without errors
- [ ] Hypotheses documented in notebook markdown cells (at least 3 explicit hypotheses)
- [ ] No model training in EDA notebook (EDA is analysis only)

---

## Phase: Experiment

- [ ] Random seed set before ANY random operation (`SEED = 42; np.random.seed(SEED); random.seed(SEED)`)
- [ ] MLflow run started with `mlflow.start_run()`
- [ ] All hyperparameters logged with `mlflow.log_param()` — no magic numbers in training loop
- [ ] Metrics logged per epoch/fold with `mlflow.log_metric()` (not just final value)
- [ ] Model artifact logged with `mlflow.log_model()` or `mlflow.sklearn.log_model()`
- [ ] Git commit SHA logged as MLflow tag
- [ ] Run name set with `mlflow.set_tag("mlflow.runName", ...)`

---

## Phase: Validate

- [ ] Final evaluation on held-out test set (never touched before this step)
- [ ] Bias/fairness check run (at minimum: check metric parity across key subgroups)
- [ ] Reproducibility check: cleared kernel + re-run all cells passes without errors
- [ ] Results match or exceed the target metric defined at experiment start
- [ ] Comparison against baseline documented

---

## Phase: Handoff

- [ ] `model_card.md` filled in completely (all sections, no `{placeholder}` text remaining)
- [ ] Winning model registered in MLflow Model Registry with alias `"champion"`
- [ ] `requirements.txt` pinned (`pip freeze > requirements.txt`)
- [ ] Engineering handoff doc written: inputs, outputs, inference latency, memory requirements
- [ ] All notebooks run clean from top-to-bottom in a fresh kernel
- [ ] `nbval` test suite passes (`pytest --nbval notebooks/`)
