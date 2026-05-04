# Session 5 — Fix `python-datascience` (PARTIAL → COMPLETE)

**Phase:** 1
**Parallel with:** Sessions 1–4, 6
**Depends on:** nothing

## Current state
```
stacks/python-datascience/
├── context.md              ← good; missing discrete Architecture Shape field
├── rules/
│   ├── 000-ds-workflow.mdc
│   └── 100-notebook-standards.mdc
├── templates/
│   └── ds-starter.md       ← good; missing model-card.md
└── vibe/
    └── vibe_ds_workflow.md ← good; need second vibe doc
```
No `examples/`. No model card template despite rules mandating one.

---

## Files to Create / Update

```
stacks/python-datascience/
├── context.md                          ← UPDATE (add Architecture Shape)
├── rules/
│   ├── 000-ds-workflow.mdc             ← keep as-is (good)
│   ├── 100-notebook-standards.mdc      ← keep as-is (good)
│   ├── 200-mlflow.mdc                  ← NEW (opinionated: MLflow is standard)
│   └── 300-data-versioning.mdc         ← NEW (DVC + hash-only)
├── templates/
│   ├── ds-starter.md                   ← keep as-is
│   ├── model-card.md                   ← NEW (required by rules, was missing)
│   └── phase-checklist.md              ← NEW
├── vibe/
│   ├── vibe_ds_workflow.md             ← keep as-is
│   └── vibe_experiment_philosophy.md   ← NEW
└── examples/
    └── iris-pipeline/
        ├── 01_eda.ipynb        (stub — markdown cells showing structure)
        ├── 02_experiment.ipynb (stub)
        ├── model_card.md       (filled example)
        └── requirements.txt
```

---

## File Specifications

### `context.md` addition

Add section:
```markdown
## Architecture Shape
Notebook — Jupyter-first for exploration; .py modules for reusable pipelines.
Not an HTTP service. Deliverable is a model card + reproducible experiment, not a running server.
See `python-spark` stack for Databricks/PySpark pipelines.
See `python-dbt-snowflake` stack for SQL analytics engineering.
```

### `rules/200-mlflow.mdc`

Frontmatter: `description: MLflow experiment tracking — mandatory`, `alwaysApply: true`

Rules:
- **MLflow is the standard**: use `mlflow.start_run()` for every experiment. Plain CSV logs are a fallback only when MLflow is explicitly unavailable.
- **Log everything**: params (hyperparameters, data path, feature set), metrics (train/val/test per epoch or per run), artifacts (model file, confusion matrix, feature importance plot).
- **Run naming**: use `mlflow.set_tag("mlflow.runName", f"{model_type}_{dataset}_{date}")` so runs are identifiable without opening them.
- **Model registration**: after validation, register winning model with `mlflow.register_model()`. Set alias `"champion"` on the production version.
- **Reproducibility**: log `git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"])` as a tag on every run. Log random seed as a param.
- **No magic numbers**: every hyperparameter passed to `mlflow.log_param()`, never hardcoded in the training loop.

### `rules/300-data-versioning.mdc`

Frontmatter: `description: Data versioning and raw data hygiene`, `alwaysApply: true`

Rules:
- **DVC is the standard**: use `dvc add data/raw/` to version raw datasets. `dvc push` to remote storage (S3, GCS, or Azure Blob). Commit `.dvc` pointer files, not data files.
- **No raw data in git**: `data/raw/` and `data/processed/` are gitignored. Only `.dvc` pointer files, `data/README.md`, and hash files are committed.
- **Hash fallback**: when DVC is not available (teaching contexts), log `sha256sum data/raw/{file}` as an MLflow tag at experiment start.
- **Processed data is reproducible**: processed data is never committed. The processing notebook/script must be re-runnable from raw data to reproduce exactly.
- **Data README**: `data/README.md` documents each dataset: source, date retrieved, schema, rows, license.

### `templates/model-card.md` (NEW — critical missing file)

```markdown
# Model Card: {Model Name}

## Model Details
- **Model type**: {e.g., RandomForestClassifier, XGBRegressor}
- **Training date**: {YYYY-MM-DD}
- **Framework**: {scikit-learn 1.x / pytorch 2.x}
- **MLflow run ID**: {run-id}
- **Git commit**: {sha}
- **Random seed**: {seed value}

## Intended Use
- **Primary use**: {what task this model solves}
- **Out-of-scope uses**: {what it should NOT be used for}
- **Users**: {who will use this}

## Data
- **Training dataset**: {name, source, date, rows, features}
- **Validation dataset**: {name, split strategy}
- **Test dataset**: {name, held-out, never touched until final evaluation}
- **Known biases**: {any known biases in the data}

## Performance
| Metric | Train | Validation | Test |
|---|---|---|---|
| {metric 1} | | | |
| {metric 2} | | | |

## Limitations
- {List known limitations}

## Ethical Considerations
- {Any fairness, privacy, or misuse concerns}

## Reproducibility
- [ ] Seed set: `SEED = {value}` in all notebooks
- [ ] Requirements pinned: `requirements.txt` or `environment.yml` committed
- [ ] Data hash logged in MLflow
- [ ] Notebook runs top-to-bottom from clean kernel
- [ ] `nbval` or equivalent confirms clean re-run
```

### `templates/phase-checklist.md`

**Phase: Explore (EDA):**
- [ ] Raw data added with DVC (`dvc add`)
- [ ] `data/README.md` documents dataset
- [ ] EDA notebook runs top-to-bottom
- [ ] Hypotheses documented in notebook markdown cells
- [ ] No model training in EDA notebook

**Phase: Experiment:**
- [ ] Random seed set before ANY random operation
- [ ] MLflow run started with `mlflow.start_run()`
- [ ] All hyperparameters logged with `mlflow.log_param()`
- [ ] Metrics logged per epoch/fold with `mlflow.log_metric()`
- [ ] Model artifact logged with `mlflow.log_model()` or `mlflow.sklearn.log_model()`

**Phase: Validate:**
- [ ] Final evaluation on held-out test set (never touched before this step)
- [ ] Bias/fairness check run (at minimum: check metric parity across key subgroups)
- [ ] Reproducibility check: cleared kernel + re-run all cells passes

**Phase: Handoff:**
- [ ] `model_card.md` filled in completely
- [ ] Winning model registered in MLflow Model Registry
- [ ] `requirements.txt` pinned (`pip freeze > requirements.txt`)
- [ ] Engineering handoff doc written (inputs, outputs, inference latency, memory requirements)

### `vibe/vibe_experiment_philosophy.md`

Sections:
- **Why EDA before modeling**: every skipped EDA step is a wasted experiment. Data always lies. Explore assumptions before testing them.
- **Hypothesis-driven experimentation**: never run a model "to see what happens." Write the hypothesis (what you expect and why) before running. Log it as an MLflow tag.
- **The reproducibility contract**: if another data scientist cannot reproduce your result from the git repo + DVC remote alone, the experiment doesn't count. No "it worked on my machine."
- **When to stop iterating**: diminishing returns — if the last 3 experiments improved the metric by <1%, validate what you have instead of optimizing further. Ship, measure, iterate.
- **What "done" looks like**: model card complete + test set evaluation run once + engineering handoff doc written + MLflow run tagged "champion". Not "accuracy is high."
- **Local vs Databricks/Spark**: this stack is for local/sklearn experiments. When data doesn't fit in memory, or when you need distributed feature engineering, move to the `python-spark` stack. Don't fight pandas with 100GB datasets.

### `examples/iris-pipeline/`

Four files demonstrating the complete EDA → experiment → model card flow:
- `01_eda.ipynb` — stub notebook with correct section structure (markdown headers, EDA cells, hypothesis section)
- `02_experiment.ipynb` — stub showing MLflow run, seed setting, param/metric logging, model artifact logging
- `model_card.md` — filled example using the iris dataset (RF classifier, accuracy/F1 on test set, known limitations)
- `requirements.txt` — pinned: scikit-learn, pandas, numpy, matplotlib, mlflow, nbval

---

## Acceptance Criteria

- [ ] `ls stacks/python-datascience/rules/` shows 4 files (000, 100, 200, 300)
- [ ] `ls stacks/python-datascience/templates/` shows `ds-starter.md`, `model-card.md`, `phase-checklist.md`
- [ ] `ls stacks/python-datascience/vibe/` shows 2 docs
- [ ] `ls stacks/python-datascience/examples/iris-pipeline/` shows 4 files
- [ ] `templates/model-card.md` has Reproducibility checklist section
- [ ] `rules/200-mlflow.mdc` states "MLflow is the standard" explicitly
- [ ] `rules/300-data-versioning.mdc` mentions DVC as the standard tool
- [ ] `context.md` has `## Architecture Shape` = "Notebook"
- [ ] `vibe_experiment_philosophy.md` contains "When to stop iterating" section
