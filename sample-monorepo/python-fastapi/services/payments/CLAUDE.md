# CLAUDE.md — payments service

FastAPI service that owns payment records and the refund decision. Nothing
else in the repo decides refunds; gateway only forwards requests here.

## Routes

| Route | Request body | Response |
|---|---|---|
| `POST /refunds` | `RefundRequest` | `RefundResult` (both defined in `contracts/refund.schema.json`) |

## Refund decision table

Evaluated against the stored payment referenced by `payment_id`:

| Condition | Decision |
|---|---|
| Payment exists, status `completed`, requested amount ≤ payment amount | `approved` |
| `payment_id` unknown | `rejected` |
| Payment status is `pending` or `refunded` | `rejected` |
| Requested amount > payment amount | `rejected` |

Rejected results carry a machine-readable rejection reason as an extra
field — the schema lists required fields only and permits extras.

## Integration point

Every decision, approved or rejected, emits exactly one
`NotificationEvent` (`contracts/notification.schema.json`) to notifications
at `http://localhost:${NOTIFICATIONS_PORT}/events`. `event_type` is
`refund.approved` or `refund.rejected`; `recipient` is the payment's
`customer_email`. That is this service's only outbound call.

## Commands (from this directory)

```bash
../../.venv/bin/python3 -m pip install -r requirements.txt        # deps
../../.venv/bin/python3 -m uvicorn src.main:app --port "$PAYMENTS_PORT"
../../.venv/bin/python3 -m pytest tests/                          # tests
```

Tests stub the notifications call; they must pass with no other service
running.

## Layout

- `src/main.py` — FastAPI app and route wiring
- `src/refunds.py` — the decision logic (the table above)
- `src/store.py` — in-memory payment records
- `tests/test_refund_logic.py` — decision tests, notifications call stubbed
- `fixtures/payment_completed.json` — a `completed` Payment sample
- `fixtures/refund_result.json` — valid `RefundResult` sample
- `requirements.txt` — this service's dependencies
