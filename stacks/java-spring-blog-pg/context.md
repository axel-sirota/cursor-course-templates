# Project Context: Java Spring Boot + PostgreSQL (blog flavor)

Custom stack derived from the `blog` reference app in this repo. Captures its peculiarities and swaps the in-memory repositories for PostgreSQL via Spring Data JPA.

## Tech Stack
- **Language**: Java 17
- **Framework**: Spring Boot 3.4.0 (`spring-boot-starter-web`, `-validation`, `-data-jpa`)
- **Build Tool**: Maven
- **Database**: PostgreSQL 16 (Spring Data JPA + Flyway migrations)
- **Testing**: JUnit 5, Mockito, Spring MockMvc, Testcontainers (`postgres:16-alpine`)
- **Codegen**: Lombok 1.18.34, MapStruct 1.5.5
- **Container**: Docker + docker-compose (app + postgres)

## Peculiarities (different from the generic `java-spring` stack)
- Java **17**, not 21 — Lombok still pulls its weight (records are used for DTOs only)
- **DTOs are records, entities are mutable `@Entity` classes**. JPA cannot manage records.
- Repository pattern uses a **package-private interface + concrete impl** (`JpaPostRepository implements PostRepository`) so the service depends on a narrow domain interface, not `JpaRepository` directly. Keeps the door open for swapping the persistence layer without touching the service.
- Custom error envelope: `ErrorResponse(Instant timestamp, int status, String error, String message)` — not Spring's `ProblemDetail`.
- Domain exceptions live in `shared/` (`NotFoundException`) and are translated centrally by `GlobalExceptionHandler`.
- Test naming convention: `method_whenCondition_thenOutcome` (e.g. `create_whenBlankFields_thenReturns400`).
- No `@Autowired` on fields — `@RequiredArgsConstructor` everywhere.
- Package-by-feature: `posts/`, `comments/`, `shared/`. No `controller/`, `service/`, `repository/` cross-cutting packages.

## Vibe & Style
- camelCase methods, PascalCase classes, 4-space indent
- Constructor injection only
- DTOs immutable (records); entities mutable for JPA; mapper is the only crossing point
- One `GlobalExceptionHandler` for the whole app
- `@Transactional` on service methods only; `@Transactional(readOnly = true)` on read paths

## Architecture Shape
REST API — Spring Boot layered architecture with package-by-feature. Controller → Service → domain Repository interface → JPA implementation → PostgreSQL.

## Package Structure
```
src/main/java/com/example/blog/
    posts/
        PostController.java
        PostService.java
        PostRepository.java         (domain interface, package-private)
        JpaPostRepository.java      (Spring Data JPA, package-private)
        Post.java                   (@Entity, mutable)
        PostDto.java                (record, public API)
        PostMapper.java             (MapStruct)
    comments/
        ... same shape
    shared/
        GlobalExceptionHandler.java
        NotFoundException.java
        ErrorResponse.java
    BlogApplication.java

src/main/resources/
    application.yml
    db/migration/
        V1__init.sql
```

## Active Phase
- Current: Phase 0 (Skeleton)
