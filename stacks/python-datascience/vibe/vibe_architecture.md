# Vibe: Data Science Architecture

## The Core Distinction — Science vs Engineering

A data science project is not a software engineering project. The deliverable is not a service — it is an **artifact**: a trained model, a report, a validated hypothesis. The architecture serves reproducibility and explainability, not scalability and uptime.

This means:
- **Notebooks are first-class** — not prototypes to be "productionized away." A well-structured notebook IS the deliverable.
- **The pipeline is linear** — data in → features → model → evaluation → output. Not event-driven, not RESTful.
- **Reproducibility > performance** — a model that runs in 10 minutes with a fixed seed is worth more than one that runs in 5 minutes but gives different results each time.

## When python-datascience Over Alternatives

**Use python-datascience when:**
- The deliverable is a trained model, a report, or an experiment result — not a production service
- The team is 1–3 data scientists working in notebooks
- The dataset fits in memory on a single machine (< ~10GB)
- You need sklearn, statsmodels, or classical ML — not distributed training

**Use python-spark instead when:**
- Data doesn't fit in memory (> 10GB typical, > 100GB definitely)
- You need distributed feature engineering for a feature store
- You're on Databricks or a cluster

**Use python-mlops instead when:**
- The model needs to ship to a production serving endpoint
- You need automated retraining pipelines
- Multiple models need versioning, A/B testing, and rollback

**Use python-dbt-snowflake instead when:**
- Your "feature engineering" is SQL transformations on a warehouse
- The output is a table or view, not a model artifact

## Notebook Architecture — The Three-Notebook Pattern

Structure every project as three notebooks in sequence:

```
notebooks/
  01_eda.ipynb          ← Explore. Understand distributions, missingness, outliers.
  02_features.ipynb     ← Engineer. Create, validate, and version features.
  03_model.ipynb        ← Train. Experiment, evaluate, select, log to MLflow.
```

Each notebook is self-contained: it reads from `data/` and writes to `data/processed/` or logs to MLflow. Notebooks do not import each other. Common functions are extracted to `src/`.

## The src/ Pattern

When a function is used in more than one notebook, extract it to `src/`:
```
src/
  features.py    ← feature engineering functions (pure, tested)
  evaluation.py  ← metric computation (pure, tested)
  data.py        ← data loading utilities
```

`src/` functions must be:
- **Pure**: same input → same output, no side effects
- **Tested**: pytest tests in `tests/`
- **Typed**: full type hints

Notebooks call `src/` functions. `src/` never imports from notebooks.

## MLflow as the Experiment Database

Every training run is logged. No silent experiments. The MLflow run IS the record of what was tried:
- `mlflow.log_params()` — hyperparameters
- `mlflow.log_metrics()` — evaluation results
- `mlflow.log_artifact()` — trained model, confusion matrix, feature importance plot

Local tracking URI (`sqlite:///mlruns.db`) for solo work. Databricks-managed MLflow for team work.

## Data Directory Contract

```
data/
  raw/          ← never modified, never committed if large (gitignore + DVC)
  processed/    ← output of 02_features.ipynb; committed if small
  fixtures/     ← tiny test samples, always committed
```

Raw data is read-only. Processed data is the output of a reproducible pipeline. Fixtures are the smallest possible representative sample for tests.

## When NOT to Use a Notebook

- If you're building a REST API → python-fastapi
- If you're building an automated pipeline → python-mlops or python-spark
- If the output is a SQL table → python-dbt-snowflake
- If your notebook is > 500 lines → extract to src/ and restructure
