# CLAUDE.md — gateway service

Express entry point for the public API. Validates incoming refund requests
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
npm install    # deps
npm start      # serves on $GATEWAY_PORT
npm test       # tests
```

Tests stub the payments call; they must pass with no other service running.

## Layout

- `src/index.js` — Express app and route wiring
- `src/refunds.js` — request validation and forwarding to payments
- `test/refunds.test.js` — route tests, payments call stubbed
- `fixtures/refund_request.json` — valid `RefundRequest` sample
- `package.json` — this service's dependencies and scripts
