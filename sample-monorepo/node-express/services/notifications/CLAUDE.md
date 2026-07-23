# CLAUDE.md — notifications service

Express service that records customer-facing notifications. It consumes
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
npm install    # deps
npm start      # serves on $NOTIFICATIONS_PORT
npm test       # tests
```

Tests must pass with no other service running.

## Layout

- `src/index.js` — Express app and route wiring
- `src/events.js` — event validation and log appending
- `test/events.test.js` — accept/reject and log-line tests
- `fixtures/notification_event.json` — valid `NotificationEvent` sample
- `package.json` — this service's dependencies and scripts
- `notifications.log` — runtime output, created on first accepted event; never commit it
