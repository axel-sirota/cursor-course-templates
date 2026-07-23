"""Gateway refund tests: no network, payments is faked via monkeypatch.

TestClient talks to the app in-process; the outbound call to payments is the
module-level httpx.post in src/refunds.py, which each test replaces. TestClient
itself uses an httpx.Client instance internally, so patching httpx.post never
interferes with the test transport.
"""
import sys
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.main import app  # noqa: E402

client = TestClient(app)

VALID_REQUEST = {"payment_id": "pay_001", "amount": 50, "reason": "damaged item"}


def test_refund_happy_path_relays_payments_response(monkeypatch):
    result = {
        "refund_id": "ref_001",
        "payment_id": "pay_001",
        "status": "approved",
        "processed_at": "2026-01-15T10:00:00Z",
    }
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json))
        return httpx.Response(200, json=result)

    monkeypatch.setattr(httpx, "post", fake_post)

    response = client.post("/refunds", json=VALID_REQUEST)

    assert response.status_code == 200
    assert response.json() == result
    assert len(calls) == 1
    assert calls[0][1] == VALID_REQUEST


def test_refund_relays_payments_status_code_verbatim(monkeypatch):
    rejection = {
        "refund_id": "ref_002",
        "payment_id": "pay_001",
        "status": "rejected",
        "processed_at": "2026-01-15T10:05:00Z",
    }

    def fake_post(url, json=None, timeout=None):
        return httpx.Response(200, json=rejection)

    monkeypatch.setattr(httpx, "post", fake_post)

    response = client.post("/refunds", json=VALID_REQUEST)

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_refund_payments_down_returns_502(monkeypatch):
    def fake_post(url, json=None, timeout=None):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "post", fake_post)

    response = client.post("/refunds", json=VALID_REQUEST)

    assert response.status_code == 502
    assert "payments service unreachable" in response.json()["detail"]


def test_refund_missing_field_returns_422_and_never_calls_payments(monkeypatch):
    def fail_post(*args, **kwargs):
        raise AssertionError("payments must not be called for an invalid body")

    monkeypatch.setattr(httpx, "post", fail_post)

    response = client.post("/refunds", json={"payment_id": "pay_001"})

    assert response.status_code == 422
