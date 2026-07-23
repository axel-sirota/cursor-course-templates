# gateway

Public entry point of the refund flow: validates `RefundRequest` bodies against
`contracts/refund.schema.json` (422 on malformed input), forwards valid ones to
payments at `PAYMENTS_URL` (default `http://localhost:8001`), and relays the
`RefundResult` unchanged. It makes no refund decision itself.

```bash
python3 -m venv .venv && .venv/bin/python3 -m pip install -r requirements.txt
GATEWAY_PORT=8000 .venv/bin/uvicorn src.main:app --port 8000  # from services/gateway/
.venv/bin/python3 -m pytest tests/                            # no network needed
```
