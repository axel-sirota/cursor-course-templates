# Phase Checklist: Python MLOps Pipeline

Use this checklist to track progress through each development phase.

---

## Phase 0 — Skeleton

- [ ] `pyproject.toml` with all pinned deps (mlflow, scikit-learn, xgboost, pandera, prefect, fastapi, pydantic-settings, pytest, ruff, mypy)
- [ ] MLflow experiment name defined in `shared/config.py`, tracking URI configurable via env var
- [ ] Directory structure in place: `src/training/`, `src/serving/`, `src/shared/`, `tests/unit/`, `tests/integration/`, `data/fixtures/`
- [ ] `pipeline.py` stub with `mlflow.start_run()` context manager, `log_params`, `log_metrics` placeholders
- [ ] `serving/main.py` stub with `/health` endpoint returning `{"status": "ok"}`
- [ ] Pandera schema defined for training data (even if columns are placeholders)
- [ ] `conftest.py` sets `MLFLOW_TRACKING_URI` to `sqlite:///tmp/test.db` for all tests
- [ ] `pytest --collect-only` shows test structure with no import errors (tests may skip)
- [ ] `ruff check` passes on the skeleton
- [ ] `.env.example` committed with all required env vars documented

---

## Phase 1 — Training Pipeline

- [ ] Feature engineering functions complete in `features.py`
- [ ] All feature functions have full type hints and return `pd.DataFrame`
- [ ] Unit tests for every feature function pass (`tests/unit/test_features.py`)
- [ ] Data validation passes on `data/fixtures/train_sample.csv`
- [ ] Pandera schema tested with both valid and invalid fixtures
- [ ] Model trains on fixture data, all params logged to MLflow
- [ ] Evaluation gate implemented: `evaluate_model(metric)` raises if below `settings.min_auc_threshold`
- [ ] `data_hash` and `git_commit` tags logged on every run
- [ ] `requirements.txt` artifact logged on every run
- [ ] Model registered in MLflow registry when evaluation gate passes
- [ ] Integration test: `test_pipeline.py` runs full pipeline on fixture, asserts run created + model registered
- [ ] No magic numbers: all thresholds in `shared/config.py`

---

## Phase 2 — Serving Layer

- [ ] `/predict` endpoint returns correct Pydantic response schema
- [ ] Model loads from registry by `name + stage` (never from file path)
- [ ] `/health` returns model name, stage, and `run_id`
- [ ] `lifespan` context manager loads model once at startup, not per request
- [ ] Serving unit tests pass with `FastAPI TestClient` (`tests/integration/test_serving.py`)
- [ ] Bad input returns HTTP 422 (Pydantic validation)
- [ ] Unavailable model (not loaded) returns HTTP 503
- [ ] Docker serving image builds: `docker build -f docker/Dockerfile.serving .`
- [ ] Docker serving container starts and `/health` returns 200

---

## Phase 3 — Production Readiness

- [ ] CI pipeline configured: `ruff check` → `mypy` → `pytest` → serving smoke test
- [ ] Model card artifact committed to MLflow registry for the current Production version
  - Model card includes: training data source, eval metrics, known limitations, intended use
- [ ] Drift detection stub: input schema validated on every `/predict` request
- [ ] Latency test passes: p99 < 100ms on 100 sequential requests (`tests/integration/test_serving.py`)
- [ ] Training performance test: fixture training completes in < 60 seconds
- [ ] `mypy --strict` passes on `src/serving/` with zero errors
- [ ] No hardcoded paths: all paths come from `shared/config.py` or env vars
- [ ] `mlruns/` and `.env` are in `.gitignore`
- [ ] README documents: how to run training, how to promote a model, how to start the serving server

---

## Handoff

- [ ] All tests green: unit + integration + serving
- [ ] `ruff check` zero warnings
- [ ] `mypy --strict` zero errors on serving layer
- [ ] Model card artifact present in MLflow registry for Production version
- [ ] Rollback procedure documented: which MLflow CLI command demotes the current Production version
- [ ] Retraining trigger documented: schedule, drift threshold, or manual
- [ ] Docker images for training and serving build cleanly from a fresh checkout
