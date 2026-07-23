"""In-memory payment store for the payments service.

No database on purpose: the labs are about multi-agent workflows, not
persistence. The seed data covers every row of the refund decision matrix
(one completed, one pending, one already refunded payment), and each record
carries exactly the fields required by ``contracts/payment.schema.json``.
"""

from typing import Optional

PAYMENTS: dict[str, dict] = {
    "pay-001": {
        "id": "pay-001",
        "amount": 100.0,
        "currency": "USD",
        "status": "completed",
        "customer_email": "ada@example.com",
    },
    "pay-002": {
        "id": "pay-002",
        "amount": 45.0,
        "currency": "EUR",
        "status": "pending",
        "customer_email": "grace@example.com",
    },
    "pay-003": {
        "id": "pay-003",
        "amount": 80.0,
        "currency": "ARS",
        "status": "refunded",
        "customer_email": "alan@example.com",
    },
}


def get_payment(payment_id: str) -> Optional[dict]:
    """Return the payment record for ``payment_id``, or ``None`` if unknown."""
    return PAYMENTS.get(payment_id)
