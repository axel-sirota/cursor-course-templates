# CLAUDE.md — payments service

Express service that owns payment records and the refund decision. Nothing
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
npm install    # deps
npm start      # serves on $PAYMENTS_PORT
npm test       # tests
```

Tests stub the notifications call; they must pass with no other service
running.

## Layout

- `src/index.js` — Express app and route wiring
- `src/refunds.js` — the decision logic (the table above)
- `src/store.js` — in-memory payment records
- `test/refund_logic.test.js` — decision tests, notifications call stubbed
- `fixtures/payment_completed.json` — a `completed` Payment sample
- `fixtures/refund_result.json` — valid `RefundResult` sample
- `package.json` — this service's dependencies and scripts
