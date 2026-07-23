"""Notifications service entry point.

Listens on NOTIFICATIONS_PORT (default 8002) and exposes:
- GET  /health  — liveness probe
- POST /events  — record a NotificationEvent (see src/events.py)
- GET  /events  — replay the recorded events
"""
import os

from fastapi import FastAPI

from src.events import router

app = FastAPI(title="notifications")
app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "notifications"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("NOTIFICATIONS_PORT", "8002"))
    uvicorn.run(app, host="127.0.0.1", port=port)
