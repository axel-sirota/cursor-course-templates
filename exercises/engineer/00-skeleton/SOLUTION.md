# Phase 00 instructor notes

No full implementation here on purpose. These notes cover what to look for while students work.

## Key design decisions

| Decision | Why |
|---|---|
| The contract is given, not designed | The track teaches contract-first delivery with Cursor. Letting `/architect` redesign the API breaks grading. If a student's interface contract differs from `openapi.yaml`, stop and fix that before the skeleton. |
| Stubs return contract shapes, not `{}` | An always-200 server must fail the grader. The skeleton grader checks types (`isString`, `isInteger`, `isCollection`), so the student has to read the schema. |
| Same grader works on the finished app | The walk registers, logs in and uses the returned token. Mocks accept any token; the real app gets a real one. Phase 00 stays green forever and catches regressions in shape. |
| Ids are strings in JSON | Removes the 53-bit integer problem for JavaScript clients and lets every stack use its natural key type internally. Java and Go students serialize `Long` / `int64` keys as strings. |

## Common mistakes

| Symptom in the grader | Cause |
|---|---|
| S-02 fails with 200 | Framework default status. FastAPI needs `status_code=201`, Spring needs `ResponseEntity.status(CREATED)` or `@ResponseStatus`, Express and Nest need an explicit `res.status(201)` / `@HttpCode` check. |
| S-11 or S-14 fails with 200 | Delete returns 200 with a body. The contract says 204 and no body. |
| S-02 `isString` on `id` fails | Numeric ids leaked into JSON. |
| S-05 fails on `tags` | Field omitted when empty. The contract requires `tags: []` from day one. |
| S-06 fails on `items` | List returns a bare array instead of the envelope. |
| S-03 fails on `tokenType` | Lowercase `bearer`. The contract says `Bearer`. |
| Connection refused | Server on the stack default port (8080, 3000) instead of 8000. Either set the port or export `BASE_URL`. See STACK_NOTES. |

## What good looks like

- One handler file (or controller) per resource, matching the stack layout in STACK_NOTES.
- Mock data in one place (a fixtures module), not copied into every handler.
- A README line in the workspace with the exact start command.
- go-grpc: proto copied to `proto/blog/v1/blog.proto`, `buf lint` clean, health and reflection registered.

## Timing

Most students spend half the time on `/architect` review. That is fine. Push them to read the session files before approving, especially the acceptance criteria lines.
