# notifications

Records customer-facing notifications. Payments emits a `NotificationEvent`
(see `contracts/notification.schema.json`) on every refund decision; this
service validates it and appends it to `notifications.log`. Rejected events
are never logged.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe |
| POST | `/events` | Record a `NotificationEvent` (422 if it violates the contract) |
| GET | `/events` | Replay every recorded event |

## Log format

One JSON object per line (JSON Lines), exactly the accepted event payload:

```
{"event_type":"refund.approved","payment_id":"pay_001","refund_id":"ref_001","recipient":"customer@example.com"}
```

The path comes from `NOTIFICATIONS_LOG` (default `./notifications.log`),
resolved per request so tests can redirect it.

## Run

From the monorepo root, with the venv created by the getting-started steps:

```bash
.venv/bin/python3 -m pip install -r services/notifications/requirements.txt

# serve on NOTIFICATIONS_PORT (default 8002)
cd services/notifications
../../.venv/bin/python3 -m uvicorn src.main:app --port "${NOTIFICATIONS_PORT:-8002}"

# tests
../../.venv/bin/python3 -m pytest tests/
```

> **Heads up:** `fixtures/notification_event.json` is intentionally broken —
> Demo 6 has `contracts/validate.sh` reject it so an agent can fix it live.
> The service code itself is contract-correct; only that fixture is not.
