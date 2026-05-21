# Spring Boot Development Lifecycle

## Maven Lifecycle

The standard Maven lifecycle phases used in this stack:

| Phase | Command | What It Does |
|---|---|---|
| Compile | `mvn compile` | Compiles production code; runs annotation processors (MapStruct, Lombok) |
| Test | `mvn test` | Runs unit and slice tests (`@WebMvcTest`, `@DataJpaTest`) |
| Verify | `mvn verify` | Runs all tests + integration tests + Spotless format check |
| Package | `mvn package` | Produces the fat JAR in `target/` |

Always use `mvn verify` (not just `mvn test`) before merging. It catches integration test failures and formatting violations that `mvn test` skips.

## Local Development

### Run directly with Maven wrapper
```bash
./mvnw spring-boot:run
```
Picks up `src/main/resources/application.properties` (or `application-dev.properties` with `-Dspring.profiles.active=dev`).

### Run with Docker Compose (recommended)
```bash
docker compose up
```
Starts the app container alongside PostgreSQL. Use this to simulate the production environment locally.

Sample `docker-compose.yml`:
```yaml
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/appdb
      - SPRING_DATASOURCE_USERNAME=app
      - SPRING_DATASOURCE_PASSWORD=secret
      - SPRING_PROFILES_ACTIVE=dev
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 5s
      timeout: 5s
      retries: 5
```

## Feature Branch Workflow

1. `git checkout -b feature/TICKET-name`
2. Write failing test first (TDD)
3. Implement until green
4. Run `mvn verify` locally — must pass
5. Push branch, open PR
6. CI runs `mvn verify` — must pass before merge
7. Merge to `main`
8. Deploy from `main`

## Database Migration Discipline

Flyway manages schema evolution. Files live in:
```
src/main/resources/db/migration/
    V1__create_users_table.sql
    V2__add_email_index.sql
    V3__create_orders_table.sql
```

Rules:
- **Never modify an existing migration file** once it has been applied to any environment. Flyway checksums each file and will refuse to start if a file changes.
- **Always add a new migration** for schema changes. Even in development, keep migrations append-only.
- Prefix with `V{n}__description.sql` (two underscores before the description).
- Migrations run automatically on application startup (`spring.flyway.enabled=true` by default).

## CI Configuration (GitHub Actions example)

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
          cache: maven
      - run: mvn verify
```
