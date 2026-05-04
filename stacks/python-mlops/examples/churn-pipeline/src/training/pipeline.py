from __future__ import annotations

import hashlib
import subprocess

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from src.shared.config import settings
from src.training.evaluate import evaluate_model
from src.training.features import compute_features
from src.training.validate import validate_training_data

PARAMS = {
    "n_estimators": 200,
    "max_depth": 4,
    "learning_rate": 0.05,
    "random_state": settings.random_seed,
}


def run_pipeline(data_path: str) -> str:
    df = pd.read_csv(data_path)
    validate_training_data(df)
    features = compute_features(df)
    X = features.drop("churned", axis=1)
    y = features["churned"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=settings.random_seed)

    mlflow.set_experiment(settings.mlflow_experiment_name)
    with mlflow.start_run() as run:
        mlflow.log_params(PARAMS)
        mlflow.set_tags({
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
            "data_hash": hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest(),
        })

        model = GradientBoostingClassifier(**PARAMS)
        model.fit(X_train, y_train)

        auc = roc_auc_score(y_val, model.predict_proba(X_val)[:, 1])
        mlflow.log_metric("val_auc", auc)

        evaluate_model(auc)  # raises if below threshold

        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            input_example=X_val.head(5),
            registered_model_name=settings.model_name,
        )
    return run.info.run_id
