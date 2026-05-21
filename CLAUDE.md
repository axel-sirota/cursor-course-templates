# Project Context: broker

> **Persona is MANDATORY.** Start with `/set-persona`. Then the SDD pipeline is:
> `/set-persona → /setup-stack (engineer / ds / devops only; designer + pm skip) → /architect → /start-session → /next-session`
> Use `/undo persona | stack | all` to roll back installs.

## Active Persona
data-scientist

## Active Client
(none)

## Active Stack
java-spring (detected — reuses existing `stacks/java-spring/` rules and templates)

## Architecture Shape
REST API — Spring Boot layered + feature-package architecture. Per feature: Controller → Service → Repository → Entity/DTO. Cross-cutting concerns in `shared/`.

## Active Phase
Phase 0 (Skeleton)

## Tech Stack
- Language: Java 17
- Framework: Spring Boot 3.4.0 (Web, WebFlux, Data JPA, Validation)
- Database: PostgreSQL + Flyway migrations
- Build: Maven
- Testing: JUnit Jupiter, Spring Boot Test, Testcontainers (Postgres)
- Linting: Spotless + Google Java Format
- Extras: MapStruct, Hypersistence Utils

## Detected Style
- Architecture: Layered + feature-packages (`messages/`, `topics/`, `subscriptions/`, `dispatch/`, `deadletter/`, `shared/`)
- Naming: PascalCase classes; suffixes `Controller` / `Service` / `Repository` / `Dto`
- Indentation: 2 spaces (Google Java Format)
- DI: Constructor injection only (no field `@Autowired`)
- DTOs: Nested static classes (e.g. `MessageDto.Response`, `MessageDto.PublishRequest`)

## Key Rules
- Constructor injection only — no `@Autowired` on fields
- Group code by feature package, not by layer
- Integration tests use Testcontainers Postgres, not H2
- Run `mvn spotless:apply` before commit
- Flyway migrations live in `src/main/resources/db/migration/V<n>__name.sql`

## Strictness: Low
- Refactoring: Only touch what is necessary
- New Code: Apply full standards to new features only
- Legacy Code: Document issues but don't force refactoring

## Stack Source
Existing rules and examples live in [stacks/java-spring/](stacks/java-spring/). Not re-installed into `.claude/rules/` — refer to `stacks/java-spring/rules/` directly, or run `/setup-stack java-spring` to copy them in.
