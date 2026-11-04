# Stack notes

Same Blog API, six stacks. This page tells you how to make your stack meet the contract in `contract/openapi.yaml` and pass the Hurl graders. Your code lives in `workspaces/engineer/`.

**Requirements:** your stack's own toolchain plus [Hurl](https://hurl.dev) 7 or newer. go-grpc also needs [grpcurl](https://github.com/fullstorydev/grpcurl). No Python is needed to grade.

## Summary

| Stack | Usual port | Make it listen on 8000 | Contract copy goes in | Run your own tests | Id type inside / in JSON |
|---|---|---|---|---|---|
| python-fastapi | 8000 | `uvicorn app.main:app --port ${PORT:-8000}` | `workspaces/engineer/contract/openapi.yaml` | `pytest` | `int` or `uuid.UUID` / string |
| go-gin | 8080 | `r.Run(":" + getenv("PORT", "8000"))` | `workspaces/engineer/api/openapi.yaml` | `go test ./...` | `int64` or `uuid.UUID` / string (`json:"id,string"` for int64) |
| go-grpc | 50051 (gRPC) | `GRPC_ADDR=localhost:50051`, listen on `:${PORT:-50051}` | `workspaces/engineer/proto/blog/v1/blog.proto` | `go test ./...` and `buf lint` | `int64` or UUID / string in proto |
| java-spring | 8080 | `server.port=${PORT:8000}` in `application.yml` | `workspaces/engineer/src/main/resources/static/openapi.yaml` | `./mvnw test` | `Long` or `UUID` entity / `String` in DTO records |
| node-express | 3000 | `app.listen(Number(process.env.PORT ?? 8000))` in `src/server.ts` | `workspaces/engineer/contract/openapi.yaml` | `npm test` | number or UUID / string |
| node-nestjs | 3000 | `await app.listen(process.env.PORT ?? 8000)` in `src/main.ts` | `workspaces/engineer/contract/openapi.yaml` | `npm test` and `npm run test:e2e` | number or UUID / string |

If you keep your stack's usual port, point the grader at it instead: `BASE_URL=http://localhost:8080 exercises/engineer/run-acceptance.sh 02`.

Treat the contract copy as read-only. If your framework generates its own spec (FastAPI `/openapi.json`, springdoc `/v3/api-docs`, Nest Swagger), diff it against the copy as a review step, but the copy wins.

## Traps that every stack hits

| Rule | Trap |
|---|---|
| A-05, P-05 | The framework's default validation error has the wrong status (400) or the wrong body. Build one global error handler that emits `{"error":{"code","message","fields":[{"field","message"}]}}`. |
| A-05 | `fields[].field` must be the camelCase JSON name (`pageSize`), not the Java field, Go struct field or Python attribute name. |
| A-21 | Missing token is 401, not 403. |
| P-10 | Unknown ids of any format are 404. Typed path parameters (UUID, integer) usually return 400 or 422 on bad input. Map that to 404. |
| P-13 | Ownership (403) is checked before body validation (422). Framework binding validates first, so validate the body explicitly after the ownership check, or accept a loose DTO. |
| S-02 | Ids are strings in JSON. |
| X-11 | Malformed JSON is 400 `MALFORMED_JSON`; wrong types inside valid JSON are 422. |

## python-fastapi

- **Run:** `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.
- **camelCase JSON:** give schemas `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` and return models with `by_alias` (FastAPI does this with `response_model`).
- **422 shape:** FastAPI already uses 422 but with `{"detail":[...]}`. Register an exception handler for `RequestValidationError` that builds the envelope. Map each error's `loc` to the alias name. If the error type is `json_invalid`, return 400 `MALFORMED_JSON` instead (X-11).
- **Ids in the path:** declare `post_id: str`, not `UUID` or `int`, or bad formats become 422 instead of 404 (P-10).
- **Query params:** `page: int = Query(1, ge=1)` produces 422 automatically, but the field name comes from `loc`; check it says `page`.
- **Auth:** `HTTPBearer` returns 403 when the header is missing on some FastAPI versions. Use `HTTPBearer(auto_error=False)` and raise your own 401.
- **Hashing:** passlib is unmaintained and breaks with bcrypt 4.x. Use `bcrypt` directly or `pwdlib`.
- **JWT:** PyJWT `jwt.decode(token, key, algorithms=["HS256"])`. Always pass `algorithms`.
- **405:** FastAPI returns 405 already; add a handler for `StarletteHTTPException` so 404 and 405 use the envelope, and keep the `Allow` header.

## go-gin

- **Run:** `go run ./cmd/app` with `PORT` read from the environment, default `8000`.
- **Body errors:** `c.ShouldBindJSON` returns `*json.SyntaxError` for broken JSON (400 `MALFORMED_JSON`), `*json.UnmarshalTypeError` for wrong types (422) and `validator.ValidationErrors` for rule breaks (422).
- **Field names:** register `validate.RegisterTagNameFunc` to report the `json` tag name, not the Go field name.
- **Blank strings:** `binding:"required"` accepts `"   "`. Trim and check in the service (P-06).
- **Empty arrays:** a nil slice marshals to `null`. Initialize `Tags: []string{}` (S-05, T-02).
- **404 and 405:** set `r.HandleMethodNotAllowed = true`, then `r.NoRoute` and `r.NoMethod` handlers that write the envelope (X-10, X-13).
- **JWT:** golang-jwt `jwt.Parse(tok, keyFunc, jwt.WithValidMethods([]string{"HS256"}))`.
- **CORS:** `gin-contrib/cors` with an explicit `AllowOrigins` list from `CORS_ORIGINS`. Do not use `AllowAllOrigins` (X-18).

## go-grpc

- **Run:** listen on `:50051` (or `PORT`). Register `grpc.health.v1.Health` and server reflection.
- **Contract:** copy `contract/grpc/blog.proto` to `proto/blog/v1/blog.proto` so `buf lint` package-directory rules pass. Generate with `buf generate`. Never edit generated code.
- **Grader:** `GRPC_ADDR=localhost:50051 exercises/engineer/run-acceptance.sh <phase> --grpc` runs `contract/grpc/grpc_smoke.sh` with grpcurl. It checks the same rules by name with a `G-` prefix (`G-P12` is `P-12`).
- **Status codes:** INVALID_ARGUMENT for 400/422, UNAUTHENTICATED for 401, PERMISSION_DENIED for 403, NOT_FOUND for 404, ALREADY_EXISTS for 409. The mapping is at the top of the proto.
- **Auth:** read metadata key `authorization` (lowercase) in a unary interceptor. Skip it for Register, Login and reads.
- **Zero values:** proto3 sends `0` for an unset `page`. Treat 0 as "use the default", negative as INVALID_ARGUMENT.
- **Tags on update:** proto3 cannot tell an absent repeated field from an empty one, so `UpdatePostRequest` has `replace_tags`.
- **HTTP graders (stretch):** add grpc-gateway with `google.api.http` annotations that map each RPC to the contract path. Then the Hurl suites run against the gateway port too. Phase 05 CORS and request-id rules only apply to the gateway.

## java-spring

- **Run:** `./mvnw spring-boot:run` with `server.port: ${PORT:8000}`. Testcontainers needs Docker running.
- **Validation status:** `@Valid` failures raise `MethodArgumentNotValidException` (400 by default). Map it in your `@ControllerAdvice` to 422 with `fields` from `getFieldErrors()`.
- **Malformed vs wrong type:** both arrive as `HttpMessageNotReadableException`. Inspect the cause: `JsonParseException` is 400 `MALFORMED_JSON`; `MismatchedInputException` / `InvalidFormatException` is 422 on the field from `getPath()`.
- **No coercion:** Jackson turns `42` into `"42"` by default (P-08). Set `spring.jackson.mapper.allow-coercion-of-scalars: false`.
- **Ids in the path:** take `@PathVariable String id` and parse in the service, or handle `MethodArgumentTypeMismatchException` as 404 (P-10).
- **Security:** Spring Security sends 403 for anonymous users. Configure an `AuthenticationEntryPoint` that writes 401 with the envelope (A-21), and an `AccessDeniedHandler` for 403. Permit `GET /api/posts/**`, `GET /api/tags/**`, `/health`, register and login.
- **JWT:** jjwt `Jwts.parser().verifyWith(key)` or Nimbus with `JWSAlgorithm.HS256` only.
- **404 page:** turn off the Whitelabel page and handle `NoResourceFoundException` (Boot 3.2+) to return the envelope (X-10).
- **JPA:** set `spring.jpa.open-in-view: false`, map to DTO records inside `@Transactional` services.
- **Empty lists:** initialize collections so `tags` serializes as `[]`, never `null`.

## node-express

- **Run:** `npm run dev` or `node dist/server.js` with `PORT` default 8000.
- **Malformed JSON:** `express.json()` throws a `SyntaxError` with `status 400` and `type 'entity.parse.failed'`. Catch it in the error middleware and write the envelope (X-11).
- **Validation:** Zod `safeParse`; map `issue.path.join('.')` to `field`. Use `z.string().trim().min(1)` for "not blank".
- **Query params:** they are strings. `z.coerce.number().int().min(1)` for `page`; non-numeric becomes 422 (P-24).
- **Async errors:** Express 4 does not catch rejected promises. Use Express 5 or wrap handlers, or a thrown error hangs the request.
- **405:** Express returns 404 for a wrong method. Add `.all()` on each route that responds 405 with `Allow` (X-13), then a final 404 middleware.
- **JWT:** `jsonwebtoken.verify(token, secret, { algorithms: ['HS256'] })`.
- **Hashing:** `bcrypt` (native) or `bcryptjs`; both truncate at 72 bytes, so validate length first.
- **Prisma:** `BigInt` ids do not serialize to JSON; convert to string in the mapper.
- **CORS:** `cors({ origin: allowedList })`. `origin: true` reflects any origin (X-18).

## node-nestjs

- **Run:** `npm run start:dev`, `app.listen(process.env.PORT ?? 8000)`.
- **Validation status:** `ValidationPipe` returns 400. Pass `exceptionFactory` that throws `UnprocessableEntityException` with the `fields` array built from `ValidationError.property`.
- **Mass assignment:** `whitelist: true` strips `authorId` from the body (good, P-03). Do not set `forbidNonWhitelisted`, or the spoofed field becomes a 400.
- **No coercion:** `transform: true` with `enableImplicitConversion: true` turns `42` into `"42"` (P-08). Keep implicit conversion off; use `@Type(() => Number)` only on query DTOs.
- **Ids in the path:** `ParseUUIDPipe` and `ParseIntPipe` return 400. Take a plain string and return 404 from the service (P-10).
- **Envelope:** one global `@Catch()` exception filter for every error, including Nest's own `NotFoundException` and body-parser errors.
- **Status codes:** `@HttpCode(204)` on deletes, `@HttpCode(200)` on login (Nest defaults POST to 201).
- **JWT:** `passport-jwt` with `algorithms: ['HS256']`; a guard, never a check inside a controller.
- **405:** not built in. Add a fallback controller or middleware for known paths (X-13).
- **CORS:** `app.enableCors({ origin: allowedList })`.
