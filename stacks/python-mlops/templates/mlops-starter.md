# MLOps Pipeline Starter Template

Use this scaffold when creating a new MLOps project from scratch.

---

## Directory Structure

```
{project-name}/
  src/
    training/
      pipeline.py        # orchestrates full training run
      features.py        # pure feature engineering functions
      validate.py        # Pandera schema + distribution checks
      evaluate.py        # metric threshold gates
    serving/
      main.py            # FastAPI app with lifespan model load
      schemas.py         # Pydantic request/response models
      loader.py          # mlflow.pyfunc.load_model() wrapper
    shared/
      config.py          # pydantic-settings (env var backed)
      logging.py         # structured logging setup
  tests/
    conftest.py          # MLflow tmp tracking URI fixture
    unit/
      test_features.py   # pure function tests, no MLflow
      test_validate.py   # Pandera schema tests
    integration/
      test_pipeline.py   # full pipeline with local MLflow
      test_serving.py    # FastAPI TestClient
  data/
    fixtures/
      train_sample.csv   # small fixed fixture for CI (10–50 rows)
      validation.csv     # held-out fixture for eval gate tests
  docker/
    Dockerfile.training  # training image
    Dockerfile.serving   # serving image (smaller, no training deps)
  .env.example
  pyproject.toml
  mlruns/                # gitignored — local MLflow tracking store
```

---

## `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "{project-name}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "mlflow==2.14.0",
    "scikit-learn==1.5.0",
    "xgboost==2.1.0",
    "pandera==0.19.0",
    "prefect==3.0.0",
    "fastapi==0.111.0",
    "uvicorn[standard]==0.30.0",
    "pydantic-settings==2.2.0",
    "pandas>=2.1.0",
    "numpy>=1.26.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest==8.0.0",
    "pytest-mock==3.14.0",
    "ruff==0.5.0",
    "mypy==1.10.0",
    "types-requests",
]

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: fast, no external deps",
    "integration: requires local MLflow",
    "serving: requires model artifact",
    "slow: > 10s, skip on CI unless --run-slow",
]
```

---

## Example `conftest.py`

```python
import os
import pytest


@pytest.fixture(autouse=True, scope="session")
def mlflow_test_tracking(tmp_path_factory):
    """Point all MLflow calls at a throwaway SQLite DB for the test session."""
    db = tmp_path_factory.mktemp("mlruns") / "test.db"
    os.environ["MLFLOW_TRACKING_URI"] = f"sqlite:///{db}"
    yield
    os.environ.pop("MLFLOW_TRACKING_URI", None)
```

---

## Example `pipeline.py` Skeleton

```python
from __future__ import annotations

import hashlib
import subprocess

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split

from src.shared.config import settings
from src.training.evaluate import evaluate_model
from src.training.features import compute_features
from src.training.validate import validate_training_data


PARAMS: dict[str, object] = {
    "n_estimators": 200,
    "max_depth": 4,
    "learning_rate": 0.05,
    "random_state": settings.random_seed,
}


def run_pipeline(data_path: str) -> str:
    """Run full training pipeline. Returns MLflow run_id."""
    df = pd.read_csv(data_path)

    # Gate 1: data validation
    validate_training_data(df)

    features = compute_features(df)
    X = features.drop(settings.target_column, axis=1)
    y = features[settings.target_column]
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=settings.random_seed
    )

    mlflow.set_experiment(settings.mlflow_experiment_name)

    with mlflow.start_run() as run:
        # Log reproducibility metadata first
        mlflow.log_params(PARAMS)
        mlflow.set_tags({
            "git_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"]
            ).decode().strip(),
            "data_hash": hashlib.md5(
                pd.util.hash_pandas_object(df).values
            ).hexdigest(),
            "triggered_by": "ci",
        })

        # Train
        from sklearn.ensemble import GradientBoostingClassifier
        model = GradientBoostingClassifier(**PARAMS)  # type: ignore[arg-type]
        model.fit(X_train, y_train)

        # Evaluate — Gate 2: metric threshold
        from sklearn.metrics import roc_auc_score
        auc = roc_auc_score(y_val, model.predict_proba(X_val)[:, 1])
        mlflow.log_metric("val_auc", auc)
        evaluate_model(auc)  # raises ValueError if below threshold

        # Gate 3 passed (data validation was Gate 1) — register
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            input_example=X_val.head(5),
            registered_model_name=settings.model_name,
        )
        mlflow.log_artifact("requirements.txt")

    return run.info.run_id
```

---

## Example `serving/main.py` (FastAPI with lifespan)

```python
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.shared.config import settings

_model: mlflow.pyfunc.PyFuncModel | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    global _model
    _model = mlflow.pyfunc.load_model(
        f"models:/{settings.model_name}/{settings.model_stage}"
    )
    yield
    _model = None


app = FastAPI(title=f"{settings.model_name} Prediction API", lifespan=lifespan)


class PredictRequest(BaseModel):
    # Override with project-specific fields
    feature_1: float
    feature_2: float


class PredictResponse(BaseModel):
    probability: float
    predicted_class: int


@app.get("/health")
def health() -> dict[str, Any]:
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "status": "ok",
        "model_name": settings.model_name,
        "model_stage": settings.model_stage,
        "run_id": _model.metadata.run_id,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    df = pd.DataFrame([request.model_dump()])
    prob = float(_model.predict(df)[0])
    return PredictResponse(probability=prob, predicted_class=int(prob > 0.5))
```

---

## Example Pandera Schema

```python
import pandera as pa
from pandera import Column, DataFrameSchema

FEATURE_SCHEMA = DataFrameSchema(
    {
        "entity_id": Column(str, nullable=False),
        "numeric_feature_1": Column(float, pa.Check.ge(0)),
        "numeric_feature_2": Column(float, pa.Check.between(0, 1)),
        "integer_feature": Column(int, pa.Check.ge(0)),
        "target": Column(int, pa.Check.isin([0, 1])),
    },
    coerce=True,
)


def validate_training_data(df: pd.DataFrame) -> None:
    """Raise pandera.errors.SchemaError if df does not conform to schema."""
    FEATURE_SCHEMA.validate(df)
```

---

## Docker Multi-Stage

### `docker/Dockerfile.training`

```dockerfile
FROM python:3.11-slim AS base
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

FROM base AS training
COPY src/ src/
COPY data/ data/
ENTRYPOINT ["python", "-m", "src.training.pipeline"]
```

### `docker/Dockerfile.serving`

```dockerfile
FROM python:3.11-slim AS base
WORKDIR /app

# Serving only — no training deps (no sklearn fit, no prefect)
RUN pip install --no-cache-dir \
    mlflow==2.14.0 \
    fastapi==0.111.0 \
    uvicorn[standard]==0.30.0 \
    pydantic-settings==2.2.0 \
    pandas>=2.1.0

FROM base AS serving
COPY src/serving/ src/serving/
COPY src/shared/ src/shared/
EXPOSE 8000
CMD ["uvicorn", "src.serving.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> Keep the serving image small: no scikit-learn, no training orchestration deps. The model artifact is loaded from the MLflow registry at startup, not baked into the image.

---

## `.env.example`

```dotenv
# MLflow
MLFLOW_TRACKING_URI=sqlite:///mlruns.db
MLFLOW_EXPERIMENT_NAME=project/model-family

# Model Registry
MODEL_NAME=project-target
MODEL_STAGE=Production

# Training thresholds
MIN_AUC_THRESHOLD=0.75
RANDOM_SEED=42

# Optional: Databricks-managed MLflow
# MLFLOW_TRACKING_URI=databricks
# DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
# DATABRICKS_TOKEN=dapi...
```
