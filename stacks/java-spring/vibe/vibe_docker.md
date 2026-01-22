# Docker Containerization Guide (Java Spring Boot)

This guide covers Docker containerization patterns for Spring Boot applications following the vibe coding methodology.

## Why Docker?

1. **Reproducible Environments**: "Works on my machine" becomes "works everywhere"
2. **Local Dev Mirrors Production**: Same container runs locally and in production
3. **Isolation**: Dependencies don't conflict between projects
4. **Easy Onboarding**: New developers run `docker compose up` and they're ready

## Quick Start

### Generate Docker Config

Run the `/dockerize` command:

```
/dockerize
```

This creates:

- `Dockerfile` - Multi-stage build for your app
- `docker-compose.yml` - Local dev with app + database
- `.dockerignore` - Excludes unnecessary files
- `.env.example` - Environment variable template
- `/actuator/health` endpoint (Spring Boot default)

### Run Your App

```bash
# Start everything
docker compose up --build

# View logs
docker compose logs -f app

# Stop
docker compose down

# Reset database
docker compose down -v
```

## File Overview

### Dockerfile (Maven)

Multi-stage build pattern:

```dockerfile
# Build stage
FROM maven:3.9-eclipse-temurin-21-alpine AS builder
WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline -B

COPY src ./src
RUN mvn package -DskipTests -B

# Runtime stage
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

RUN addgroup -g 1001 -S app && adduser -S -u 1001 app -G app
USER app

COPY --from=builder --chown=app:app /app/target/*.jar app.jar

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

Key features:

- **JRE only**: Runtime stage uses `eclipse-temurin:21-jre-alpine`
- **Container-aware JVM**: `UseContainerSupport` and `MaxRAMPercentage`
- **Longer start period**: 30s for Spring Boot warmup
- **Actuator health**: Uses Spring Boot's built-in health endpoint

### docker-compose.yml

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/app
      - SPRING_DATASOURCE_USERNAME=postgres
      - SPRING_DATASOURCE_PASSWORD=postgres
      - SPRING_PROFILES_ACTIVE=dev
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]

volumes:
  postgres_data:
```

## Spring Boot Configuration

### Enable Actuator Health

Add to `application.properties`:

```properties
management.endpoints.web.exposure.include=health
management.endpoint.health.show-details=always
```

Or `application.yml`:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health
  endpoint:
    health:
      show-details: always
```

## JVM Container Settings

```dockerfile
# Important JVM flags for containers
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
```

- `UseContainerSupport`: JVM respects container memory limits
- `MaxRAMPercentage=75.0`: Use 75% of container memory for heap

## Common Commands

| Command | What It Does |
|---------|--------------|
| `docker compose up --build` | Build and start all services |
| `docker compose logs -f app` | Follow app logs |
| `docker compose down -v` | Stop and reset database |
| `./mvnw package -DskipTests` | Build JAR locally |

## Build Tool Variants

### Maven

```dockerfile
FROM maven:3.9-eclipse-temurin-21-alpine AS builder
RUN mvn package -DskipTests -B
```

### Gradle

```dockerfile
FROM gradle:8-jdk21-alpine AS builder
RUN gradle build -x test --no-daemon
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Out of memory" | Increase `MaxRAMPercentage` or container limits |
| "Slow startup" | Increase health check `start-period` |
| "Connection refused to DB" | Wait for `service_healthy` condition |
| "Actuator not found" | Add spring-boot-starter-actuator dependency |

## Best Practices

1. **JRE not JDK**: Use `eclipse-temurin:21-jre-alpine` for runtime
2. **Container-aware JVM**: Always set `UseContainerSupport`
3. **Longer start period**: Spring Boot needs 20-30s to start
4. **Layered JARs**: For better Docker layer caching
5. **Non-root user**: Security requirement
6. **Actuator health**: Use built-in health endpoint
