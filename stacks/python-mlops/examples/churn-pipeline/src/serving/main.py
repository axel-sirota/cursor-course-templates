from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.shared.config import settings

model: mlflow.pyfunc.PyFuncModel | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    global model
    model = mlflow.pyfunc.load_model(f"models:/{settings.model_name}/Production")
    yield
    model = None


app = FastAPI(title="Churn Prediction API", lifespan=lifespan)


class PredictRequest(BaseModel):
    tenure_days: int
    monthly_spend: float
    support_tickets: int


class PredictResponse(BaseModel):
    churn_probability: float
    predicted_churn: bool


@app.get("/health")
def health() -> dict[str, Any]:
    if model is None:
        raise HTTPException(503, "Model not loaded")
    meta = model.metadata
    return {"status": "ok", "model_name": settings.model_name, "run_id": meta.run_id}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    if model is None:
        raise HTTPException(503, "Model not loaded")
    df = pd.DataFrame([request.model_dump()])
    prob = float(model.predict(df)[0])
    return PredictResponse(churn_probability=prob, predicted_churn=prob > 0.5)
