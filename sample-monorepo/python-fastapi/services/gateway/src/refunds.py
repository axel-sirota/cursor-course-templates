"""Refunds router: accept a RefundRequest, forward it to payments, relay the answer.

The gateway makes no refund decision of its own. It validates the body against
the shared contract (contracts/refund.schema.json), forwards it to the payments
service, and returns whatever payments answered, status code and body unchanged.
"""
import os

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter()


class RefundRequest(BaseModel):
    """Mirrors the RefundRequest definition in contracts/refund.schema.json."""

    payment_id: str
    amount: float = Field(ge=0)
    reason: str


def payments_url() -> str:
    """Base URL of the payments service, read per request so tests can override it."""
    return os.environ.get("PAYMENTS_URL", "http://localhost:8001")


@router.post("/refunds")
def create_refund(refund: RefundRequest):
    """Forward a valid RefundRequest to payments and relay the RefundResult."""
    url = payments_url()
    try:
        response = httpx.post(f"{url}/refunds", json=refund.model_dump(), timeout=5.0)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"payments service unreachable at {url}: {exc}",
        )
    return JSONResponse(status_code=response.status_code, content=response.json())
