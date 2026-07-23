# gateway

Public HTTP entry point. `GET /health` for liveness; `POST /refunds` validates
the body against `contracts/refund.schema.json` (422 on failure) and forwards
it to payments at `PAYMENTS_URL` (default `http://localhost:8001`), returning
the payments response unchanged. No refund decisions happen here — payments
owns those. Listens on `GATEWAY_PORT` (default 8000).

```bash
npm install && npm start   # run the service; npm test for the test suite
```
