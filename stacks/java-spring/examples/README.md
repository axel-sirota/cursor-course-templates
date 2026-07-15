# Reference Solution: Blog API

**TEACHER ONLY** - Complete working example for reference

## What This Is
A complete Spring Boot blog application implementing the session-based workflow. Use this to:
- Understand the complete structure
- Reference during demos
- Debug student issues
- Prepare for sessions

## Features Implemented
- User registration and login (JWT, BCrypt-hashed passwords, real Postgres persistence)
- Create blog posts
- Get post by ID
- List posts, paginated
- Add comments to posts
- List comments for a post

## Quick Start
```bash
cd examples/blog-api
cp .env.example .env
sdk use java 21-tem
docker compose up -d postgres
./mvnw spring-boot:run
```

Visit: http://localhost:8080/swagger-ui.html

## Structure
Follows the exact `vibe_java_spring_boilerplate.md` structure:
- `config/` — OpenApiConfig, SecurityConfig, WebConfig
- `web/` — REST controllers + DTO records
- `service/` — business logic, `@Transactional`
- `repository/` — Spring Data `JpaRepository` interfaces
- `model/` — `@Entity` classes
- `security/` — JwtService, JwtAuthFilter, DatabaseUserDetailsService
- `exception/` — `@RestControllerAdvice`
- `src/test/` — controller, unit, and Testcontainers integration tests

## Phases Implemented
- Phase 0: Skeleton with mocks (superseded by this completed reference tree)
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

All tests pass with real Postgres integration (Testcontainers) — see
`examples/blog-api/src/test/README.md` for the full test-layer breakdown.
