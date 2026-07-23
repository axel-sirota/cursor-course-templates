"""Gateway service: public HTTP entry point of the refund monorepo.

Exposes GET /health for liveness checks and mounts the refunds router.
Run from services/gateway/ with: uvicorn src.main:app --port 8000
"""
from fastapi import FastAPI

from src.refunds import router

app = FastAPI(title="gateway")


@app.get("/health")
def health():
    """Liveness probe used by the labs to confirm the service is up."""
    return {"status": "ok", "service": "gateway"}


app.include_router(router)
