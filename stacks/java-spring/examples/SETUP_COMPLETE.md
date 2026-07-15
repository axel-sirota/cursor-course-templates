# Reference Solution - Setup Complete!

## What's Ready

A complete, working Spring Boot blog application using **Spring Data JPA + Flyway** against
real PostgreSQL, with JWT authentication.

### Location
```
examples/blog-api/
```

### Status
- Maven wrapper present (`./mvnw`)
- JDK 21 (Temurin) pinned as the build target
- Docker PostgreSQL running (host port 5433)
- Application starts successfully (`./mvnw spring-boot:run`)
- Flyway migrations apply automatically on startup
- All code follows the layered `web/service/repository/model` architecture

## Quick Start

```bash
cd examples/blog-api

# Start Docker Postgres
docker compose up -d postgres

# Pin the JDK (if not already active)
sdk use java 21-tem

# Run the app
./mvnw spring-boot:run

# Visit http://localhost:8080/swagger-ui.html
```

## Important Notes

### Port Configuration
- **PostgreSQL**: host port **5433** (not 5432)
  - Your local PostgreSQL is likely on 5432
  - Docker PostgreSQL here is on 5433 to avoid the conflict
- **Spring Boot**: port 8080
- **pgAdmin** (optional, `--profile tools`): port 5050

### Database Connection
```
SPRING_DATASOURCE_URL=jdbc:postgresql://127.0.0.1:5433/blog_db
```

## Architecture

### Spring Data JPA (not raw SQL)
```java
// Service layer uses Spring Data JpaRepository — no hand-written SQL
Post saved = postRepository.save(post);
```

Unlike the `python-fastapi` reference solution (which deliberately uses raw SQL with psycopg2
to teach students the SQL underneath an ORM), this Java/Spring Boot reference uses Spring Data
JPA + Hibernate — the idiomatic default for the Spring ecosystem. Flyway, not Hibernate
`ddl-auto`, owns the schema (`ddl-auto: validate`) — see `vibe_database.md` for why.

### Key Features
- **Constructor injection** everywhere (`@RequiredArgsConstructor`, never field `@Autowired`)
- **DTO/Entity separation** — controllers never see `@Entity` objects
- **`@Transactional` boundaries** on every write path in the service layer
- **`ProblemDetail` (RFC 7807)** error responses via `@RestControllerAdvice`
- **Flyway migrations** — versioned, checksum-validated schema changes

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Posts
- `POST /api/posts` - Create blog post (auth required)
- `GET /api/posts/{id}` - Get post by ID (public)
- `GET /api/posts` - List posts, paginated (public)

### Comments
- `POST /api/posts/{id}/comments` - Create comment (auth required)
- `GET /api/posts/{id}/comments` - List comments (public)

### Health
- `GET /actuator/health` - Actuator health check
- `GET /health` - Lightweight liveness check (kept from Phase 0 skeleton)

## Testing

### Run Tests
```bash
cd examples/blog-api
./mvnw test
```

### Test Files
- `src/test/java/.../web/*ControllerTest.java` - `@WebMvcTest` controller tests
- `src/test/java/.../service/*ServiceTest.java` - Mockito unit tests
- `src/test/java/.../integration/PostAndCommentScenariosIntegrationTest.java` - Detailed
  input/output-documented scenarios against real Postgres via Testcontainers ⭐
- `src/test/README.md` - Complete test documentation

## Teaching with This Solution

### Show Students
1. **Spring Data JPA patterns** in the repository layer (derived query methods vs `@Query`)
2. **Constructor injection** via `@RequiredArgsConstructor`
3. **DTO/Entity separation**: controller → DTO in/out, service → entity in/out
4. **Layered architecture**: `web/` → `service/` → `repository/` → `model/`
5. **Test-driven approach** with clear input/output documentation in Javadoc

### Key Files to Reference
- `src/main/java/.../config/SecurityConfig.java` — JWT filter chain wiring
- `src/main/java/.../security/JwtAuthFilter.java` — request-time token verification
- `src/main/java/.../service/*.java` — business logic + `@Transactional` examples
- `src/main/java/.../web/*.java` — request/response DTO conversion
- `src/test/java/.../integration/PostAndCommentScenariosIntegrationTest.java` — test examples with docs

## Deliberate Teaching Simplifications

Flagged explicitly so instructors can call them out, mirroring how the `python-fastapi`
reference solution flags its own simplifications (in-memory auth, raw SQL):

- **JWT auth is simplified**: `JwtAuthFilter` decodes the token and trusts its subject claim as
  the user id directly — it does not re-query `UserRepository` on every request. A production
  system would typically load a full `UserDetails` per request (or cache it) and support token
  revocation/refresh tokens. This keeps the security wiring readable for a first pass.
- **No `@ManyToOne`/`@OneToMany` relationships**: `Post.authorId` and `Comment.postId` are plain
  `UUID` foreign-key columns, not JPA object references, to avoid lazy-loading pitfalls before
  that topic is taught explicitly. See `vibe_database.md` and `templates/blog-entity.md` for the
  design rationale and how to graduate to real relationship mapping.
- **No refresh tokens**: access tokens are short-lived (30 minutes) with no renewal flow.
- **No rate limiting**: intentionally omitted; see `vibe_blog_guide.md`'s "Extending This
  Domain" section for how to add it.

## Stopping Services

```bash
# Stop but keep data
docker compose stop

# Stop and remove all data
docker compose down -v
```

## Troubleshooting

### Can't connect to database
- Check port 5433 (not 5432)
- Ensure Docker is running: `docker compose ps`
- Check logs: `docker compose logs postgres`

### Port already in use
- Change `SERVER_PORT` in `.env`
- Or stop the conflicting service

### App won't start
- Check `.env` exists (`cp .env.example .env`)
- Ensure `SPRING_DATASOURCE_URL` uses port 5433
- Verify Docker containers are healthy (`docker compose ps`)
- Confirm the pinned JDK is active: `java -version` should report 21

### Flyway checksum mismatch
- Never edit an already-applied migration file — see `rules/301-endpoint-phase.mdc`
- If you truly need to reset local state: `docker compose down -v` then re-run

## Next Steps

1. Application is ready to run
2. Test all endpoints at http://localhost:8080/swagger-ui.html
3. Use as reference during teaching
4. Show students the scenario tests
5. Walk through one complete flow: Controller → Service → Repository → Entity → Response DTO

## Perfect for Teaching

This solution demonstrates:
- Professional Spring Boot structure
- Spring Data JPA + Flyway (the idiomatic Spring persistence stack)
- JWT security wiring, explicitly flagged where simplified
- Test-driven development across three layers (unit, controller, integration)
- Clear layered architecture
- Complete documentation

Ready to use as teaching reference.
