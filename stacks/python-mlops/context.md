# Project Context: Python MLOps

## Architecture Shape
MLOps Pipeline — end-to-end ML lifecycle: data ingestion → training → evaluation → model registry → serving. Use for: production ML systems, model versioning, experiment tracking, automated retraining pipelines.
Use python-datascience for: exploratory analysis, prototyping, one-off notebooks.
Use python-spark for: large-scale feature engineering on distributed data.
Use python-dbt-snowflake for: SQL-first feature tables / analytics engineering.

## Tech Stack
- **Language**: Python 3.11+
- **Experiment Tracking**: MLflow 2.14+ (local or Databricks-managed)
- **Model Registry**: MLflow Model Registry (or Databricks Unity Catalog)
- **Training**: scikit-learn 1.5+, XGBoost 2.1+, or PyTorch 2.3+ (project-specific)
- **Feature Store**: Feast (open-source) or Databricks Feature Store
- **Serving**: FastAPI + mlflow.pyfunc.load_model() or BentoML
- **Pipeline Orchestration**: Prefect 3.x or Databricks Workflows
- **Data Validation**: Great Expectations 0.18+ or Pandera
- **Testing**: pytest, pytest-mock; no live MLflow in unit tests (mock the client)
- **Containerization**: Docker multi-stage; model server image separate from training image
- **Linting**: ruff (E, F, I, N, W), mypy --strict on serving layer

## Vibe & Style
- **Coding Style**: snake_case everywhere. Type hints mandatory on all public functions.
- **Architecture**: Three-layer separation — Training pipeline, Model Registry, Serving layer. Never couple training logic to serving logic.
- **Pattern**: Experiment → Register → Serve. Models are artifacts, not code. Serving loads from registry, not from source.
- **Reproducibility**: Every training run logs: dataset hash, hyperparameters, metrics, model artifact, environment (requirements.txt or conda.yaml). A run must be reproducible from its logged metadata alone.

## Key Rules
- **Log everything to MLflow**: params, metrics, artifacts, tags. No silent training runs.
- **Never load model from file path in serving**: always load from MLflow registry by name + stage (Production/Staging).
- **Data validation before training**: validate input schema and value distributions with Pandera or Great Expectations before any fit() call.
- **Model versioning**: every promoted model has a README artifact describing: training data, evaluation metrics, known limitations, intended use.
- **No raw pickle**: use mlflow.sklearn.log_model() / mlflow.pytorch.log_model() — never raw pickle.dump().
- **Serving is stateless**: model server has no database, no file writes. It loads model once at startup, serves predictions.

## Active Phase
- Current: Phase 0 (Skeleton)
