# Phase 0 — Skeleton (DONE by `/architect`)

**Goal:** Walking skeleton compiles, Flyway runs, `BrokerApplicationTests.contextLoads` is green against a Postgres testcontainer. All endpoints exist but return `501 Not Implemented` via `GlobalExceptionHandler`.

## Surface
| Method | Path | Status |
|---|---|---|
| POST   | /topics                              | 501 |
| GET    | /topics                              | 501 |
| POST   | /topics/{name}/messages              | 501 |
| POST   | /topics/{name}/subscriptions         | 501 |
| GET    | /subscriptions/{id}                  | 501 |
| DELETE | /subscriptions/{id}                  | 501 |
| GET    | /admin/dead-letter                   | 501 |
| POST   | /admin/dead-letter/{id}/replay       | 501 |

## Verify
```
mvn -B test            # contextLoads passes (needs Docker for testcontainers)
mvn -B spring-boot:run # boots; curl localhost:8080/topics -> 501
```
