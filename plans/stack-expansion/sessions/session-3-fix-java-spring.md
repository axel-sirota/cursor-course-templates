# Session 3 — Fix `java-spring` (STUB → COMPLETE)

**Phase:** 1
**Parallel with:** Sessions 1, 2, 4–6
**Depends on:** nothing

## Current state
```
stacks/java-spring/
├── context.md              ← Spring Boot 3.2.0 (stale), Java 17/21 mismatch
├── rules/
│   ├── java-standards.mdc  ← no numeric prefix
│   └── 500-docker-java.mdc
├── templates/
│   ├── Dockerfile           ← broken layer caching
│   └── java-starter.md      ← stale versions, no validation dep, no MapStruct
└── vibe/
    └── vibe_docker.md
```
No `examples/`.

---

## Files to Create / Update

```
stacks/java-spring/
├── context.md                          ← UPDATE
├── rules/
│   ├── 000-spring-workflow.mdc         ← NEW
│   ├── 100-spring-architecture.mdc     ← NEW
│   ├── 200-spring-testing.mdc          ← NEW
│   ├── 300-spring-style.mdc            ← NEW
│   ├── 400-spring-standards.mdc        ← RENAME from java-standards.mdc
│   └── 500-docker-java.mdc             ← keep as-is
├── templates/
│   ├── java-starter.md                 ← UPDATE (fix versions, add deps)
│   ├── phase-checklist.md              ← NEW
│   └── Dockerfile                      ← UPDATE (fix layer caching)
├── vibe/
│   ├── vibe_architecture.md            ← NEW
│   └── vibe_development_lifecycle.md   ← NEW
└── examples/
    └── users-resource/
        ├── User.java
        ├── UserRepository.java
        ├── UserService.java
        ├── UserController.java
        ├── UserDto.java
        └── UserControllerTest.java
```

---

## File Specifications

### `context.md` additions

Update Tech Stack versions:
- Spring Boot: `3.4.x` (not 3.2.0)
- Java: `21` everywhere (remove 17 references)
- Add: MapStruct 1.5+, Testcontainers 1.19+

Add section:
```markdown
## Architecture Shape
REST API — Spring Boot layered architecture. Controller → Service → Repository → Entity.
Also applicable to: event-driven (add spring-kafka, replace Controller with @KafkaListener), 
modular monolith (use Spring Modulith), batch processing (Spring Batch).
```

### `rules/000-spring-workflow.mdc`

Frontmatter: `description: Spring Boot TDD workflow`, `alwaysApply: true`

Rules:
- **TDD loop**: Write failing `@WebMvcTest` or `@DataJpaTest` → implement → green → refactor.
- **Test slice first**: for new endpoints use `@WebMvcTest` before `@SpringBootTest`. Faster feedback.
- **Feature branch + CI**: branch → implement → `mvn verify` passes → PR → merge.
- **No logic in `@SpringBootApplication`**: main class only wires Spring context. All config in `@Configuration` classes.
- **Actuator health**: every service exposes `/actuator/health`. Required for container health checks.

### `rules/100-spring-architecture.mdc`

Frontmatter: `description: Spring Boot layered architecture rules`, `alwaysApply: true`

Rules:
- **Layer isolation**: `@RestController` handles HTTP only — parse request, delegate to `@Service`, return response. Zero business logic in controllers.
- **DTOs at the boundary**: API layer uses DTOs (records preferred in Java 21). Entity types never leave the service layer. Map with MapStruct.
- **Service layer owns transactions**: `@Transactional` belongs on `@Service` methods, never on controllers or repositories directly.
- **Read-only transactions**: annotate read-only service methods with `@Transactional(readOnly = true)`. Allows database optimizations.
- **Repository interfaces only**: use `JpaRepository` / `CrudRepository`. No `EntityManager` in application code unless writing complex JPQL.
- **Validation at entry**: validate all incoming DTOs with `@Valid` / `@Validated`. Define constraints on DTO fields, not entity fields.
- **Global exception handling**: use `@ControllerAdvice` + `@ExceptionHandler`. Never handle exceptions in individual controllers.
- **No `@Autowired` on fields**: use constructor injection only. Immutable beans. Lombok `@RequiredArgsConstructor` is fine.

### `rules/200-spring-testing.mdc`

Frontmatter: `description: Spring Boot testing strategy`, `alwaysApply: true`

Rules:
- **Test slice strategy**:
  - `@WebMvcTest` — controller layer only. Mock the service with `@MockBean`.
  - `@DataJpaTest` — repository layer only. Uses in-memory H2 or Testcontainers Postgres.
  - `@SpringBootTest` — full context integration tests. Use sparingly (slow).
- **Testcontainers for Postgres**: `@DataJpaTest` tests that need real Postgres use Testcontainers. Annotate test class with `@Testcontainers`, field with `@Container static PostgreSQLContainer<?>`.
- **Reuse containers**: declare Postgres container as `static` to reuse across test methods in a class.
- **MockMvc for controllers**: use `MockMvc` with `perform(post(...)).andExpect(status().isCreated())`. Assert JSON with `jsonPath`.
- **No production Spring context in unit tests**: pure unit tests (service logic) use plain JUnit 5 + Mockito, zero Spring annotations.
- **Test naming**: `methodName_whenCondition_thenExpectedBehavior` format.

### `rules/300-spring-style.mdc`

Frontmatter: `description: Java/Spring code style`, `alwaysApply: true`

Rules:
- **Formatting**: Google Java Format (Spotless plugin enforces). `mvn spotless:check` in CI.
- **Records for DTOs**: prefer `record UserDto(String name, String email)` over POJO classes in Java 21+.
- **Lombok restrictions**: allowed: `@RequiredArgsConstructor`, `@Getter`, `@Setter`, `@Builder`, `@Slf4j`. Forbidden: `@Data` on entities (causes Hibernate issues), `@EqualsAndHashCode` on entities.
- **No `Optional` as method parameters**: `Optional` is for return types only.
- **Package structure**: group by feature not layer: `users/` contains `UserController`, `UserService`, `UserRepository`, `User`, `UserDto`. Not `controllers/UserController`, `services/UserService`.

### `templates/java-starter.md` (UPDATE)

Fix pom.xml:
- Spring Boot: `3.4.1`
- Java: `21`
- Add dependencies: `spring-boot-starter-validation`, `mapstruct`, `mapstruct-processor`, `testcontainers-bom`
- Add plugins: `spotless-maven-plugin` with google-java-format

Show canonical package structure by feature:
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

### `templates/Dockerfile` (UPDATE)

Fix layer caching — add `mvn dependency:go-offline` step before copying source:
```dockerfile
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -q
COPY src ./src
RUN mvn clean package -DskipTests -q
```

### `templates/phase-checklist.md`

**Phase 0 — Skeleton:**
- [ ] All controllers registered (return `501 Not Implemented`)
- [ ] Service interfaces defined
- [ ] Repository interfaces defined (extend JpaRepository)
- [ ] `mvn compile` succeeds
- [ ] `mvn spotless:check` passes

**Phase 1+ — Implementation:**
- [ ] `@WebMvcTest` written and failing before controller logic
- [ ] `@DataJpaTest` written and failing before repository logic
- [ ] `@Valid` on all request DTOs
- [ ] `@ControllerAdvice` handles expected exceptions
- [ ] `@Transactional(readOnly = true)` on all read service methods

**Handoff:**
- [ ] `mvn verify` passes (all tests green)
- [ ] `mvn spotless:check` passes
- [ ] No `@Autowired` field injection remaining
- [ ] `/actuator/health` returns 200

### `vibe/vibe_architecture.md`

Sections:
- **Why Spring Boot**: unmatched enterprise ecosystem, Spring Security, Spring Data, Spring Batch, Spring Integration. Choose Spring Boot when you need a battle-tested, heavily tooled Java web service with a large team.
- **When Quarkus instead**: GraalVM native image, sub-100ms startup, Kubernetes/serverless. If your team is Java but needs Go-like startup times, Quarkus.
- **Architecture shapes**: layered REST (this stack), event-driven (add spring-kafka), modular monolith (Spring Modulith), batch (Spring Batch). All use the same layer discipline — only the entry point changes.
- **CQRS and event sourcing**: for complex domains with high read/write asymmetry, consider CQRS. Axon Framework integrates with Spring Boot. Not required for simple CRUD — don't over-engineer.
- **Feature-based packaging**: package by feature (`users/`, `orders/`) not by layer (`controllers/`, `services/`). Makes feature extraction into microservices trivial if needed later.
- **MapStruct over manual mapping**: zero-runtime-cost compile-time mapper. Never write `UserDto dto = new UserDto(entity.getName(), ...)` by hand when MapStruct generates it.

### `vibe/vibe_development_lifecycle.md`

- Maven lifecycle: `compile` → `test` → `verify` (includes integration tests) → `package`
- Local dev: `./mvnw spring-boot:run` or Docker Compose with `docker compose up`
- Feature branch → PR → `mvn verify` in CI → merge → deploy
- Migration discipline: Flyway migrations in `src/main/resources/db/migration/`; never modify existing migrations; always add new ones

### `examples/users-resource/`

Six files showing a complete layered CRUD feature:
- `User.java` — JPA entity with `@Entity`, `@Id`, `@GeneratedValue`, fields with `@Column`
- `UserDto.java` — Java record with `@NotBlank`, `@Email` validation constraints
- `UserRepository.java` — `interface UserRepository extends JpaRepository<User, Long>`
- `UserService.java` — `@Service @Transactional` class; uses `UserRepository`; returns `UserDto`
- `UserController.java` — `@RestController @RequestMapping("/users")` with POST + GET + GET /:id
- `UserControllerTest.java` — `@WebMvcTest(UserController.class)` with `@MockBean UserService`; 3 test methods using MockMvc

---

## Acceptance Criteria

- [ ] `ls stacks/java-spring/rules/` shows 6 files (000–500)
- [ ] `ls stacks/java-spring/templates/` shows 3 files
- [ ] `ls stacks/java-spring/vibe/` shows 2 docs
- [ ] `ls stacks/java-spring/examples/users-resource/` shows 6 `.java` files
- [ ] `java-starter.md` pom pins Spring Boot `3.4.x` and Java `21`
- [ ] `rules/200-spring-testing.mdc` contains `@WebMvcTest`, `@DataJpaTest`, `Testcontainers` decision tree
- [ ] `vibe_architecture.md` contains "When Quarkus instead" section
- [ ] `Dockerfile` has `mvn dependency:go-offline` before `COPY src`
