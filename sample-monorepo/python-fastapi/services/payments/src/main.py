"""FastAPI entry point for the payments service.

Run from ``services/payments``:

    .venv/bin/python3 -m uvicorn src.main:app --port 8001

The port comes from ``PAYMENTS_PORT`` (default 8001, see ``.env.example``).
"""

import os

from fastapi import FastAPI

from src.refunds import router

app = FastAPI(title="payments")
app.include_router(router)


@app.get("/health")
def health() -> dict:
    """Liveness probe used by the labs' smoke checks."""
    return {"status": "ok", "service": "payments"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=int(os.environ.get("PAYMENTS_PORT", "8001")),
    )
