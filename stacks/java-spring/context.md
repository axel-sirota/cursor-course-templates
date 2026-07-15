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
- **TDD**: Write `@WebMvcTest` (Controller) or `@DataJpaTest` (Repo) before implementation — see `rules/400-testing-first.mdc`.
- **Service Layer**: All business logic lives in `@Service` classes, never in Controllers — see `rules/300-java-spring-style.mdc` and `rules/500-implementation.mdc`.
- **DTOs**: Always use DTOs (Data Transfer Objects) for API inputs/outputs, map to Entities in the Service layer — see `rules/100-architect-phase.mdc` for the DTO strategy decision.
- **Exceptions**: Use `@ControllerAdvice` for global error handling.
- **Session Workflow**: Architect (`rules/100-architect-phase.mdc`) → Skeleton (`rules/200-skeleton-phase.mdc`) → per-endpoint sessions (`rules/301-endpoint-phase.mdc`) → Phase Transition (`rules/600-phase-transition.mdc`); environment/tooling discipline in `rules/000-core-workflow.mdc` and `rules/000-environment-setup.mdc`; Docker packaging in `rules/500-docker-java.mdc`.

## Active Phase
- Current: Phase 0 (Skeleton)

