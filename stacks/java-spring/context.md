# Project Context: Java Spring Boot

## Tech Stack
- **Language**: Java 21
- **Framework**: Spring Boot 3.4.x
- **Build Tool**: Maven (standard `pom.xml`)
- **Database**: PostgreSQL (Spring Data JPA)
- **Testing**: JUnit 5, Mockito, Testcontainers 1.19+
- **Mapping**: MapStruct 1.5+
- **Linting**: Spotless (Google Java Format)

## Vibe & Style
- **Coding Style**: Standard Java conventions (CamelCase methods, PascalCase classes).
- **Architecture**: Layered Architecture, packaged by feature.
- **Pattern**: Constructor Injection only (`@RequiredArgsConstructor`). No `@Autowired` on fields.

## Key Rules
- **TDD**: Write `@WebMvcTest` (Controller) or `@DataJpaTest` (Repo) before implementation.
- **Service Layer**: All business logic lives in `@Service` classes, never in Controllers.
- **DTOs**: Always use DTOs (records preferred in Java 21) for API inputs/outputs. Map to Entities using MapStruct. Entity types never leave the service layer.
- **Exceptions**: Use `@ControllerAdvice` for global error handling.
- **Transactions**: `@Transactional` on service methods. `@Transactional(readOnly = true)` on all read methods.
- **Validation**: `@Valid` / `@Validated` on all incoming request DTOs.

## Architecture Shape
REST API — Spring Boot layered architecture. Controller → Service → Repository → Entity.
Also applicable to: event-driven (add spring-kafka, replace Controller with @KafkaListener),
modular monolith (use Spring Modulith), batch processing (Spring Batch).

## Package Structure (by feature)
```
src/main/java/com/example/app/
    users/
        UserController.java
        UserService.java
        UserRepository.java
        User.java          (JPA entity)
        UserDto.java       (record)
        UserMapper.java    (MapStruct interface)
    shared/
        GlobalExceptionHandler.java
        ErrorResponse.java
```

## Active Phase
- Current: Phase 0 (Skeleton)
