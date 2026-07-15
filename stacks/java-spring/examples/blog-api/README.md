# Blog API — Reference Solution

A complete Spring Boot blog application: users, posts, and comments with JWT authentication and
PostgreSQL persistence, built following the session-based phase workflow in `rules/`.

## Quick Start

```bash
cd examples/blog-api
cp .env.example .env

# Start Postgres (host port 5433 to avoid clashing with a local Postgres on 5432)
docker compose up -d postgres

# Pin the JDK if you haven't already
sdk use java 21-tem

# Run the app (Flyway migrations apply automatically on startup)
./mvnw spring-boot:run
```

Visit: http://localhost:8080/swagger-ui.html

## Endpoints

### Authentication
- `POST /api/auth/register` — register a new user, returns a JWT
- `POST /api/auth/login` — authenticate, returns a JWT

### Posts
- `POST /api/posts` — create a post (auth required)
- `GET /api/posts/{id}` — get a post by id (public)
- `GET /api/posts?page=0&size=20` — list posts, paginated (public)

### Comments
- `POST /api/posts/{postId}/comments` — comment on a post (auth required)
- `GET /api/posts/{postId}/comments` — list a post's comments (public)

### Health
- `GET /actuator/health` — Spring Boot Actuator health
- `GET /health` — lightweight liveness check (kept from the Phase 0 skeleton)

## Structure

Follows the exact `vibe_java_spring_boilerplate.md` layering:
```
src/main/java/com/example/blogapi/
├── Application.java
├── config/       — OpenApiConfig, SecurityConfig, WebConfig
├── web/          — controllers + dto/
├── service/      — business logic, @Transactional
├── repository/   — Spring Data JpaRepository interfaces
├── model/        — @Entity classes
├── security/     — JwtService, JwtAuthFilter, DatabaseUserDetailsService
└── exception/    — GlobalExceptionHandler
```

## Phases Implemented

- Phase 0: Skeleton with mock endpoints (superseded — this tree is the completed reference)
- Phase 1: `POST /api/auth/register`
- Phase 2: `POST /api/auth/login`
- Phase 3: `POST /api/posts`
- Phase 4: `GET /api/posts/{id}`
- Phase 5: `GET /api/posts` (paginated)
- Phase 6: `POST /api/posts/{id}/comments`
- Phase 7: `GET /api/posts/{id}/comments`

## Testing

```bash
./mvnw test
```

All tests pass with real Postgres integration via Testcontainers — see `src/test/README.md`
for the full breakdown of test layers.

## Authentication Simplifications

This is a **teaching-scale** JWT implementation. See `../SETUP_COMPLETE.md` for the explicit
list of simplifications versus a production auth system (no refresh tokens, no token
revocation, `JwtAuthFilter` doesn't re-hit the database per request).
