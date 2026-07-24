"""POST /refunds — the refund decision lives here and nowhere else.

Decision matrix (from ``specs/feature-refunds.md``):

| Payment lookup | Payment status  | Requested amount | Decision |
|----------------|-----------------|------------------|----------|
| not found      | —               | —                | rejected |
| found          | not `completed` | —                | rejected |
| found          | `completed`     | > payment amount | rejected |
| found          | `completed`     | <= payment amount| approved |

Responses conform to ``RefundResult`` in ``contracts/refund.schema.json``.
Approved refunds also emit a ``NotificationEvent`` (see
``contracts/notification.schema.json``) to the notifications service; a
notification failure never fails the refund itself.
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.store import get_payment

logger = logging.getLogger("payments.refunds")

router = APIRouter()

NOTIFICATIONS_URL = os.environ.get("NOTIFICATIONS_URL", "http://localhost:8002")
NOTIFICATION_TIMEOUT_SECONDS = 2.0


class RefundRequest(BaseModel):
    """Mirror of ``RefundRequest`` in contracts/refund.schema.json."""

    payment_id: str
    amount: float = Field(ge=0)
    reason: str


def decide(payment: Optional[dict], requested_amount: float) -> tuple[str, Optional[str]]:
    """Apply the decision matrix; return (status, machine-readable rejection reason)."""
    if payment is None:
        return "rejected", "payment_not_found"
    if payment["status"] != "completed":
        return "rejected", "payment_not_completed"
    if requested_amount > payment["amount"]:
        return "rejected", "amount_exceeds_payment"
    return "approved", None


def notify(event: dict) -> None:
    """Best-effort POST of a NotificationEvent to the notifications service.

    The refund is already decided when this runs, so delivery problems are
    logged and swallowed — a down notifications service must never turn an
    approved refund into an error.
    """
    try:
        response = httpx.post(
            f"{NOTIFICATIONS_URL}/events",
            json=event,
            timeout=NOTIFICATION_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning(
            "notification for refund %s not delivered: %s", event["refund_id"], exc
        )


@router.post("/refunds")
def create_refund(request: RefundRequest) -> dict:
    """Decide the refund and return a RefundResult."""
    payment = get_payment(request.payment_id)
    status, rejection_reason = decide(payment, request.amount)

    result = {
        "refund_id": "ref-" + uuid.uuid4().hex[:8],
        "payment_id": request.payment_id,
        "status": status,
        "processed_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
    }
    if rejection_reason is not None:
        result["reason"] = rejection_reason

    if status == "approved":
        notify(
            {
                "event_type": "refund.approved",
                "payment_id": payment["id"],
                "refund_id": result["refund_id"],
                "recipient": payment["customer_email"],
            }
        )

    return result
