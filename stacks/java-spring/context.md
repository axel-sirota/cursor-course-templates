# Project Context: Java Spring Boot

## Tech Stack
- **Language**: Java 17+
- **Framework**: Spring Boot 3+
- **Build Tool**: Maven (standard `pom.xml`)
- **Database**: PostgreSQL (Spring Data JPA)
- **Testing**: JUnit 5, Mockito, Testcontainers
- **Linting**: Checkstyle, Spotless

## Vibe & Style
- **Coding Style**: Standard Java conventions (CamelCase methods, PascalCase classes).
- **Architecture**: Layered Architecture.
  - `web/` (Controllers)
  - `service/` (Business Logic)
  - `repository/` (Data Access Interfaces)
  - `model/` (JPA Entities)
- **Pattern**: Dependency Injection (@Autowired/Constructor Injection).

## Key Rules
- **TDD**: Write `@WebMvcTest` (Controller) or `@DataJpaTest` (Repo) before implementation.
- **Service Layer**: All business logic lives in `@Service` classes, never in Controllers.
- **DTOs**: Always use DTOs (Data Transfer Objects) for API inputs/outputs, map to Entities in the Service layer.
- **Exceptions**: Use `@ControllerAdvice` for global error handling.

## Active Phase
- Current: Phase 0 (Skeleton)

