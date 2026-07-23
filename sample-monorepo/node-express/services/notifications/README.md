# notifications

Records customer-facing notification events for the refund flow. `POST /events`
accepts a `NotificationEvent` (see `contracts/notification.schema.json`), rejects
contract violations with 400, and appends each accepted event as one JSON line
(`event_type`, `payment_id`, `refund_id`, `recipient`) to `notifications.log` —
override the path with `NOTIFICATIONS_LOG`. `GET /events` returns the parsed
entries; `GET /health` reports liveness. Listens on `NOTIFICATIONS_PORT` (8002).

- Run: `npm install && npm start`
- Test: `npm test`
