# Project Context: Python Data Science

## Tech Stack
- **Language**: Python 3.11+
- **Notebook**: JupyterLab 4.x
- **Data manipulation**: pandas 2.2.x, numpy 2.x
- **ML**: scikit-learn 1.5.x (default), pytorch / tensorflow (optional)
- **Visualization**: matplotlib 3.9.x, seaborn 0.13.x
- **Experiment tracking**: MLflow 2.x (local file store in `mlruns/`) plus `experiments/log.md`
- **Testing**: pytest (src/ tests), nbval (notebook runs top to bottom)
- **Linting**: ruff, nbqa (applies ruff to notebooks)
- Exact pins: `examples/iris-pipeline/requirements.txt`

## Vibe & Style
- **Coding Style**: snake_case, PEP 8
- **Architecture**: Notebook-first for exploration; .py modules for reusable pipelines
- **Data flow**: raw → processed → features → model → evaluation

## Key Rules
- Seed every experiment before any random operation
- No raw data committed: paths and hashes only
- Notebooks run top to bottom (clear + re-run before handoff)
- Every model beats a logged baseline
- Log every experiment in `experiments/log.md` with params, metrics, seed and artifact paths
- Model card required before handoff

## Entry Point & Structure
- **Entry point**: `notebooks/01_eda.ipynb` → `notebooks/02_features.ipynb` → `notebooks/03_model.ipynb` (sequential)
- **Reusable logic**: extracted to `src/features.py`, `src/evaluation.py`, `src/data.py` (pure functions, tested)
- **Directory layout**:
  ```
  notebooks/          ← analysis notebooks (numbered sequence)
  src/                ← reusable functions extracted from notebooks
  tests/              ← pytest tests for src/ functions
  data/raw/           ← read-only source data (gitignored)
  data/processed/     ← output of feature pipeline (gitignored)
  data/fixtures/      ← tiny test samples (always committed)
  experiments/log.md  ← one row per experiment (seed, params, metrics, artifact paths, MLflow run ID)
  artifacts/          ← saved models, metrics and plots per experiment
  docs/eda/           ← EDA write-ups and dataset profiles
  mlruns/             ← MLflow local tracking (gitignored)
  ```
- **Config**: environment variables via `python-dotenv` or `os.getenv()` for data paths; no pydantic-settings (not a service)
- **Persistence**: local files (Parquet/CSV) + MLflow local artifact store; no database
- **Test command**: `pytest tests/ && pytest --nbval-lax notebooks/`

## Active Phase
- Current: Explore (EDA)

## Architecture Shape
Experiment Notebook (Jupyter-first for exploration; .py modules for reusable pipelines)
Not an HTTP service. Deliverable is a model card + reproducible experiment, not a running server.
See `python-spark` stack for Databricks/PySpark pipelines.
See `python-dbt-snowflake` stack for SQL analytics engineering.
