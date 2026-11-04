# Phase 01: Authentication

**Time:** 90 to 120 minutes. **Grader:** `exercises/engineer/run-acceptance.sh 01`

## Scenario

The skeleton accepts any token. Now make auth real: users register, passwords are hashed, login returns a signed JWT, and `GET /api/auth/me` only answers to a valid token. Users are stored in your database.

## Inputs

- Contract: `exercises/engineer/contract/openapi.yaml`, operations `register`, `login`, `getMe`, schemas `RegisterRequest`, `LoginRequest`, `User`, `TokenResponse`, `Error`.
- Session file: `workspaces/engineer/plans/sessions/session-2-phase-1.md`.
- Environment: `JWT_SECRET_KEY` (required), `JWT_EXPIRATION_DAYS` (default 7), `DATABASE_URL`.

## Task

1. Persist users (id, username, email, password hash, createdAt).
2. Hash passwords with bcrypt (cost 10 or more) or argon2id. Never store or return the plain password or the hash.
3. Register: validate input, enforce unique username and email ignoring case.
4. Login: return an HS256 JWT with `sub` = user id and `exp`. Same error for unknown user and wrong password.
5. Me: read `Authorization: Bearer <token>`, verify signature, algorithm and expiry, load the user.
6. Use the standard error envelope for every error, including framework validation errors.

## Rules checked

| Rule | Requirement |
|---|---|
| A-01 | Register returns 201 and the User; username is stored as sent |
| A-02 | No response ever contains password or password hash fields |
| A-03 | Duplicate username, any case: 409 `USERNAME_TAKEN` |
| A-04 | Duplicate email, any case: 409 `EMAIL_TAKEN` |
| A-05 | Missing fields: 422 `VALIDATION_FAILED`, `fields[]` names each bad field |
| A-06 | Username matches `^[A-Za-z0-9_]{3,30}$` |
| A-07 | Email looks like an email |
| A-08 | Password is 8 to 72 bytes |
| A-10 | Login returns a three-part JWT, `tokenType: "Bearer"`, positive integer `expiresIn`, the User |
| A-11 | Wrong password: 401 `INVALID_CREDENTIALS` |
| A-12 | Unknown user: the same 401 `INVALID_CREDENTIALS` |
| A-13 | Login with a missing field: 422 |
| A-20 | Me returns the token owner |
| A-21 | No token: 401 `UNAUTHORIZED` (not 403) |
| A-22 | Garbage token: 401, not 500 |
| A-23 | Tampered signature: 401 |
| A-24 | Token signed with another secret: 401 |
| A-25 | `alg: none` token: 401 |
| A-26 | Scheme other than `Bearer`: 401 |

## Done when

- [ ] `exercises/engineer/run-acceptance.sh 01 --cumulative` passes (phases 00 and 01)
- [ ] Unit tests cover the password hasher and the token service with no HTTP and no database
- [ ] Integration tests cover register, login and me against a real database
- [ ] `JWT_SECRET_KEY` comes from the environment; the server refuses to start without it
- [ ] `/code-review` reports no Critical or High security findings

## In-session commands

- `/start-session engineer` on session 2.
- `/engineer-tasks`: expect tasks for the user table or migration, hasher, token service, register, login, me, error envelope.
- `/engineer-implement` one task at a time. The security-auditor step runs on every auth task.
- `/code-review`, then `/next-session`.

## Stretch

- Rate limit `POST /api/auth/login` per username and per IP (return 429).
- Add `POST /api/auth/refresh` with rotating refresh tokens. Keep the graded contract unchanged.
- Expired-token test: craft a token with your own secret and `exp` in the past in your unit tests.
