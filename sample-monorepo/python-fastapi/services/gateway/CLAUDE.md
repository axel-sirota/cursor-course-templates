# CLAUDE.md — gateway service

FastAPI entry point for the public API. Validates incoming refund requests
and forwards them to payments. It makes no refund decision of its own — if
a task asks for decision logic here, it belongs in payments.

## Routes

| Route | Request body | Response |
|---|---|---|
| `POST /refunds` | `RefundRequest` (`contracts/refund.schema.json`) | The `RefundResult` payments returned, status and body unchanged |

A body missing a required `RefundRequest` field returns HTTP 422, and
payments is never called for it.

## Integration point

Forwards valid requests to payments at
`http://localhost:${PAYMENTS_PORT}/refunds`. That is this service's only
outbound call.

## Commands (from this directory)

```bash
../../.venv/bin/python3 -m pip install -r requirements.txt        # deps
../../.venv/bin/python3 -m uvicorn src.main:app --port "$GATEWAY_PORT"
../../.venv/bin/python3 -m pytest tests/                          # tests
```

Tests stub the payments call; they must pass with no other service running.

## Layout

- `src/main.py` — FastAPI app and route wiring
- `src/refunds.py` — request validation and forwarding to payments
- `tests/test_refunds.py` — route tests, payments call stubbed
- `fixtures/refund_request.json` — valid `RefundRequest` sample
- `requirements.txt` — this service's dependencies
