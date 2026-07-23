"""Tests for the notifications service.

Covers the two acceptance criteria from specs/feature-refunds.md:
- a valid event results in exactly one new line in notifications.log
- an invalid event is rejected and notifications.log is untouched
"""
import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))

from src.main import app  # noqa: E402

VALID_EVENT = {
    "event_type": "refund.approved",
    "payment_id": "pay_001",
    "refund_id": "ref_001",
    "recipient": "customer@example.com",
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    """TestClient wired to a log file inside tmp_path."""
    monkeypatch.setenv("NOTIFICATIONS_LOG", str(tmp_path / "notifications.log"))
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_post_then_get_round_trip(client, tmp_path):
    post = client.post("/events", json=VALID_EVENT)
    assert post.status_code == 201

    log_file = tmp_path / "notifications.log"
    assert log_file.exists()
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == VALID_EVENT

    get = client.get("/events")
    assert get.status_code == 200
    assert get.json() == [VALID_EVENT]


def test_malformed_event_rejected_and_log_untouched(client, tmp_path):
    bad_event = dict(VALID_EVENT, event_type="refund.done")  # not in the enum
    response = client.post("/events", json=bad_event)
    assert response.status_code == 422
    assert not (tmp_path / "notifications.log").exists()


def test_missing_required_field_rejected(client, tmp_path):
    incomplete = {k: v for k, v in VALID_EVENT.items() if k != "recipient"}
    response = client.post("/events", json=incomplete)
    assert response.status_code == 422
    assert not (tmp_path / "notifications.log").exists()


def test_get_events_empty_before_any_post(client):
    response = client.get("/events")
    assert response.status_code == 200
    assert response.json() == []
