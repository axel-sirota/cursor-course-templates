# payments

Owns payment records and decides whether a refund is approved or rejected.
Listens on `PAYMENTS_PORT` (default 8001); on approval it POSTs a
`NotificationEvent` to `NOTIFICATIONS_URL` (default `http://localhost:8002`).

| Condition | Decision |
|---|---|
| Payment exists, `completed`, amount ≤ payment amount | approved |
| Unknown payment / not `completed` / amount too high | rejected + reason |

Run: `npm start` · Test: `npm test`
