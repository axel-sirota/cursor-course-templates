"""Notification events: accept, log, and replay.

POST /events validates a NotificationEvent against the shared contract
(contracts/notification.schema.json) and appends it as one JSON line to
notifications.log. GET /events reads that log back as parsed entries.

The log path comes from the NOTIFICATIONS_LOG environment variable and is
resolved on every request (not at import time) so tests can point it at a
temporary directory.
"""
import json
import os
from pathlib import Path
from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

DEFAULT_LOG_PATH = "./notifications.log"


class NotificationEvent(BaseModel):
    """Mirror of contracts/notification.schema.json — the schema wins."""

    event_type: Literal["refund.approved", "refund.rejected"]
    payment_id: str
    refund_id: str
    recipient: str


def log_path() -> Path:
    """Resolve the notifications log path from the environment."""
    return Path(os.environ.get("NOTIFICATIONS_LOG", DEFAULT_LOG_PATH))


@router.post("/events", status_code=201)
def record_event(event: NotificationEvent) -> dict:
    """Append one accepted event as a single JSON line.

    Invalid payloads never reach this function: FastAPI rejects them with
    HTTP 422 during validation, so nothing is logged for a rejected event.
    """
    path = log_path()
    with path.open("a", encoding="utf-8") as log_file:
        log_file.write(event.model_dump_json() + "\n")
    return {"status": "recorded", "event_type": event.event_type}


@router.get("/events")
def list_events() -> List[dict]:
    """Return every logged event, parsed back from the JSON-lines log."""
    path = log_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as log_file:
        return [json.loads(line) for line in log_file if line.strip()]
