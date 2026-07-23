# CLAUDE.md — notifications service

FastAPI service that records customer-facing notifications. It consumes
`NotificationEvent` payloads and appends each accepted one to
`notifications.log` — one event, one line.

## Routes

| Route | Request body | Effect |
|---|---|---|
| `POST /events` | `NotificationEvent` (`contracts/notification.schema.json`) | Appends one line to `notifications.log` |

Events that fail schema validation are rejected and nothing is logged — an
invalid event must leave `notifications.log` untouched.

## Integration point

Inbound only: payments posts events here on every refund decision. This
service calls no other service. `FAKE_SMTP_URL` from the repo `.env` is
where mail *would* be sent — it stays fake; never wire up real mail.

## Commands (from this directory)

```bash
../../.venv/bin/python3 -m pip install -r requirements.txt        # deps
../../.venv/bin/python3 -m uvicorn src.main:app --port "$NOTIFICATIONS_PORT"
../../.venv/bin/python3 -m pytest tests/                          # tests
```

Tests must pass with no other service running.

## Layout

- `src/main.py` — FastAPI app and route wiring
- `src/events.py` — event validation and log appending
- `tests/test_events.py` — accept/reject and log-line tests
- `fixtures/notification_event.json` — valid `NotificationEvent` sample
- `requirements.txt` — this service's dependencies
- `notifications.log` — runtime output, created on first accepted event; never commit it
