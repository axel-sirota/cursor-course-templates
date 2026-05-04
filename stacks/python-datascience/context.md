# Project Context: Python Data Science

## Tech Stack
- **Language**: Python 3.11+
- **Notebook**: JupyterLab / Jupyter Notebook
- **Data manipulation**: pandas 2.x, numpy 1.x
- **ML**: scikit-learn (default), pytorch / tensorflow (optional)
- **Visualization**: matplotlib, seaborn
- **Testing**: pytest (pipeline tests), nbval (notebook tests)
- **Linting**: ruff, nbqa (applies ruff to notebooks)

## Vibe & Style
- **Coding Style**: snake_case, PEP 8
- **Architecture**: Notebook-first for exploration; .py modules for reusable pipelines
- **Data flow**: raw → processed → features → model → evaluation

## Key Rules
- Seed every experiment before any random operation
- No raw data committed — paths and hashes only
- Notebooks run top-to-bottom (clear + re-run before handoff)
- Log every experiment with params, metrics, seed, and artifact paths
- Model card required before handoff

## Entry Point & Structure
- **Entry point**: `notebooks/01_eda.ipynb` → `notebooks/02_features.ipynb` → `notebooks/03_model.ipynb` (sequential)
- **Reusable logic**: extracted to `src/features.py`, `src/evaluation.py`, `src/data.py` (pure functions, tested)
- **Directory layout**:
  ```
  notebooks/          ← analysis notebooks (numbered sequence)
  src/                ← reusable functions extracted from notebooks
  tests/              ← pytest tests for src/ functions
  data/raw/           ← read-only source data (gitignored if large)
  data/processed/     ← output of feature pipeline
  data/fixtures/      ← tiny test samples (always committed)
  mlruns/             ← MLflow local tracking (gitignored)
  ```
- **Config**: environment variables via `python-dotenv` or `os.getenv()` for data paths and API keys; no pydantic-settings (not a service)
- **Persistence**: local files (Parquet/CSV) + MLflow artifact store; no database
- **Test command**: `pytest tests/`

## Active Phase
- Current: Explore (EDA)

## Architecture Shape
Notebook — Jupyter-first for exploration; .py modules for reusable pipelines.
Not an HTTP service. Deliverable is a model card + reproducible experiment, not a running server.
See `python-spark` stack for Databricks/PySpark pipelines.
See `python-dbt-snowflake` stack for SQL analytics engineering.

## Active Persona
- (set by /set-persona)
