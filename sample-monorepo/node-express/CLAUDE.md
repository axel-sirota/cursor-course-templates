# CLAUDE.md — refund monorepo (Node / Express)

Monorepo with three Express services under `services/` plus shared JSON
Schema contracts in `contracts/`. This file holds only what applies to the
whole repository — every service-specific fact (commands, routes, decision
rules) lives in that service's own `CLAUDE.md`. Read it before changing
anything under that service.

## Services

- `services/gateway` — public HTTP entry point; validates refund requests and forwards them to payments.
- `services/payments` — owns payment records; decides approve/reject on refunds.
- `services/notifications` — consumes notification events and records them.

`specs/feature-refunds.md` is the feature spec; the schemas it references
live in `contracts/`.

## Contract-first rule

Every payload that crosses a service boundary must validate against the
schemas in `contracts/`. When code, spec prose, or a fixture disagrees with
a schema, the schema wins. After changing any service's fixtures or payload
handling, run:

```bash
contracts/validate.sh services/<service>
```

Any `FAIL` line means the change is not done.

## Working conventions

- Run a service's commands from that service's directory; its `CLAUDE.md`
  lists the exact run and test commands.
- Environment comes from `.env` at the repo root (created from
  `.env.example` by `init.sh`); source it before starting a service.
- Test command shape: `npm test` inside the service directory — each
  service has its own `package.json`. To run everything, run it in each of
  the three service directories.
- Commit style: one service per commit, message
  `<scope>: <imperative summary>`, where scope is the service name or
  `contracts`.

## Port map (from .env.example)

| Env var | Service | Default |
|---|---|---|
| `GATEWAY_PORT` | gateway | 8000 |
| `PAYMENTS_PORT` | payments | 8001 |
| `NOTIFICATIONS_PORT` | notifications | 8002 |

`FAKE_SMTP_URL` (default `smtp://localhost:1025`) is a fake SMTP endpoint;
no real mail is ever sent from this repo.
