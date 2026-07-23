# payments

Owns payment records and the refund decision. Listens on `PAYMENTS_PORT` (default 8001); on approval it emits a `NotificationEvent` to `NOTIFICATIONS_URL` (default `http://localhost:8002`), and a failed notification never fails the refund.

| Payment | Status | Requested amount | Decision |
|---|---|---|---|
| missing | — | — | rejected `payment_not_found` |
| found | not `completed` | — | rejected `payment_not_completed` |
| found | `completed` | > payment amount | rejected `amount_exceeds_payment` |
| found | `completed` | <= payment amount | approved |

Run from this directory: `.venv/bin/python3 -m uvicorn src.main:app --port 8001` — tests: `.venv/bin/python3 -m pytest tests/`
