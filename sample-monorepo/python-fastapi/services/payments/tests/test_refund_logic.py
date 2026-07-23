"""Tests for the four branches of the refund decision matrix.

The notification call is mocked throughout: these tests must pass with no
notifications service running. Store seed data (``src/store.py``):
pay-001 completed 100 USD, pay-002 pending, pay-003 refunded.
"""

import sys
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.main import app  # noqa: E402

client = TestClient(app)


def post_refund(payment_id: str, amount: float):
    """POST /refunds with the notification call mocked; return (response, mock)."""
    body = {"payment_id": payment_id, "amount": amount, "reason": "customer_request"}
    with patch("src.refunds.notify") as mock_notify:
        response = client.post("/refunds", json=body)
    return response, mock_notify


def test_refund_approved_when_completed_and_amount_within_payment():
    response, mock_notify = post_refund("pay-001", 50)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved"
    assert body["payment_id"] == "pay-001"
    assert body["refund_id"].startswith("ref-")
    assert body["processed_at"].endswith("Z")

    assert mock_notify.call_count == 1
    event = mock_notify.call_args.args[0]
    assert event["event_type"] == "refund.approved"
    assert event["payment_id"] == "pay-001"
    assert event["refund_id"] == body["refund_id"]
    assert event["recipient"] == "ada@example.com"


def test_refund_rejected_when_payment_missing():
    response, mock_notify = post_refund("pay-404", 10)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["reason"] == "payment_not_found"
    assert mock_notify.call_count == 0


def test_refund_rejected_when_payment_not_completed():
    response, mock_notify = post_refund("pay-002", 10)  # pay-002 is pending

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["reason"] == "payment_not_completed"
    assert mock_notify.call_count == 0


def test_refund_rejected_when_amount_exceeds_payment():
    response, mock_notify = post_refund("pay-001", 150)  # payment amount is 100

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["reason"] == "amount_exceeds_payment"
    assert mock_notify.call_count == 0
