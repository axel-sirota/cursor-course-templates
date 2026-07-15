# Java Spring Boot Boilerplate Guide

This guide covers the standard project structure, configuration, and conventions for
Spring Boot projects following the vibe coding methodology.

## Package Layout

```
src/main/java/com/example/<app>/
├── Application.java        # @SpringBootApplication entry point
├── config/                 # @Configuration classes
│   ├── OpenApiConfig.java
│   ├── SecurityConfig.java
│   └── WebConfig.java      # CORS, interceptors
├── web/                    # @RestController — Experience layer
│   ├── HealthController.java
│   ├── PostController.java
│   └── dto/                # Request/response DTOs (records)
├── service/                # @Service — business logic
├── repository/             # Spring Data JpaRepository interfaces
├── model/                  # @Entity classes
├── security/               # JwtService, JwtAuthFilter
└── exception/               # Custom exceptions + @RestControllerAdvice
src/main/resources/
├── application.yml         # Base config
├── application-dev.yml     # Dev profile overrides
├── application-test.yml    # Test profile overrides
└── db/migration/           # Flyway migrations (V1__..., V2__...)
```

This mirrors the `web/service/repository/model` layering already described in `context.md` and
`rules/300-java-spring-style.mdc` — the package layout on disk is a direct reflection of the
architectural layering, so navigating the codebase and reasoning about dependency direction stay
in sync.

## DTO vs Entity Separation

**Never let an `@Entity` leave the service layer.** Controllers accept and return DTOs
(preferably Java `record`s); services translate between DTOs and entities.

```java
// web/dto/PostResponse.java — the API contract
public record PostResponse(UUID postId, String title, String content, UUID authorId, Instant createdAt) {
    public static PostResponse from(Post post) {
        return new PostResponse(post.getId(), post.getTitle(), post.getContent(), post.getAuthorId(), post.getCreatedAt());
    }
}

// model/Post.java — the persistence contract
@Entity
@Table(name = "posts")
public class Post {
    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    // ...
}
```

Why this matters concretely:
- Hibernate lazy-loading proxies can throw `LazyInitializationException` if an `@Entity` is
  serialized outside a transaction — DTOs sidestep this entirely
- The API contract (JSON shape) and the database schema can evolve independently
- Jackson serializing an `@Entity` directly risks accidentally exposing internal-only fields
  (password hashes, audit columns not meant for the client)

## `application.yml` Profiles

Spring Boot's profile system (`dev`/`test`/`prod`) lets one base file hold shared config while
profile-specific files override just what differs:

**application.yml (base, always loaded):**
```yaml
spring:
  application:
    name: my-app
  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:postgresql://localhost:5432/appdb}
    username: ${SPRING_DATASOURCE_USERNAME:postgres}
    password: ${SPRING_DATASOURCE_PASSWORD:postgres}
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false
  flyway:
    enabled: true
    locations: classpath:db/migration

server:
  port: ${SERVER_PORT:8080}

management:
  endpoints:
    web:
      exposure:
        include: health,info
```

**application-dev.yml (activated via `SPRING_PROFILES_ACTIVE=dev`):**
```yaml
logging:
  level:
    com.example.myapp: DEBUG
    org.hibernate.SQL: DEBUG
    org.hibernate.orm.jdbc.bind: TRACE
```

**application-test.yml (activated by `@ActiveProfiles("test")` in test classes):**
```yaml
spring:
  flyway:
    enabled: true  # Testcontainers gets a real Postgres, Flyway still applies migrations
```

Activate a profile locally:
```bash
SPRING_PROFILES_ACTIVE=dev ./mvnw spring-boot:run
```

## `open-in-view: false`

**Always disable** the Open Session in View pattern:
```yaml
spring:
  jpa:
    open-in-view: false
```

By default Spring Boot keeps the Hibernate session open for the entire HTTP request, which lets
lazy associations be fetched from the view/serialization layer — this hides `N+1` query bugs and
couples the transaction lifecycle to the web layer. Disabling it forces all data access to happen
inside `@Transactional` service methods, which is exactly the layering this stack enforces.

## `@RestControllerAdvice` Exception Handling

Centralize HTTP status mapping in one place instead of try/catch in every controller:

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(EntityNotFoundException.class)
    public ProblemDetail handleNotFound(EntityNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Resource Not Found");
        return problem;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        String detail = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, detail);
    }
}
```

`ProblemDetail` (RFC 7807) is Spring's built-in structured error response type since Spring
Framework 6 — no custom `ErrorResponse` class is required.

## Constructor Injection Conventions

```java
@Service
@RequiredArgsConstructor  // Lombok generates a constructor for every `final` field
public class PostService {

    private final PostRepository postRepository;
    private final NotificationService notificationService;

    // Spring autowires this automatically — no @Autowired needed
}
```

Never use field injection (`@Autowired private PostRepository repo;`). Constructor injection:
- Makes required dependencies explicit in the type signature
- Allows `final` fields (immutability)
- Makes unit testing trivial: `new PostService(mockRepo, mockNotifier)`
- Fails fast at application-context startup if a dependency is missing, rather than at first use

## Lombok Usage Guidance

Use Lombok to eliminate getter/setter/constructor boilerplate on classes that need mutability
(mainly `@Entity`) — **not** on DTOs, which should be immutable `record`s instead.

| Annotation | Use on | Purpose |
|-----------|--------|---------|
| `@Getter`/`@Setter` | `@Entity` classes | JPA requires a no-arg constructor + mutable fields |
| `@NoArgsConstructor` | `@Entity` classes | Required by JPA/Hibernate |
| `@RequiredArgsConstructor` | `@Service`/`@RestController`/`@Component` | Constructor injection with zero boilerplate |
| `@Builder` | Complex `@Entity` construction in tests | Readable test fixture setup |
| `@Slf4j` | Any class that logs | Generates a `private static final Logger log` field |
| `@Data` | Avoid on `@Entity` | Generates `equals()`/`hashCode()` over all fields, which is dangerous with JPA-managed collections and lazy proxies |

## Basic CORS Configuration

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("http://localhost:3000", "http://localhost:5173")
            .allowedMethods("GET", "POST", "PUT", "PATCH", "DELETE")
            .allowedHeaders("*")
            .allowCredentials(true);
    }
}
```

For production, source `allowedOrigins` from an environment variable rather than hardcoding it —
see `rules/000-core-workflow.mdc`'s secrets management section.

## Actuator Health and Info

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info
  endpoint:
    health:
      show-details: always
```

`/actuator/health` is the standard Docker/Kubernetes healthcheck target for Spring Boot apps —
see `rules/500-docker-java.mdc` for the corresponding `HEALTHCHECK` directive.

## Swagger UI / OpenAPI Docs

Add `springdoc-openapi-starter-webmvc-ui` and docs are generated automatically from your
`@RestController` and DTO annotations — no separate spec file to hand-maintain once the app
exists (the hand-written `openapi.yaml` from the Architect phase is the *design* artifact; the
generated Swagger UI is the *implementation-truth* artifact, and the two should converge).

```java
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI blogApiOpenApi() {
        return new OpenAPI()
            .info(new Info().title("Blog API").version("1.0.0"))
            .components(new Components().addSecuritySchemes("bearerAuth",
                new SecurityScheme().type(SecurityScheme.Type.HTTP).scheme("bearer").bearerFormat("JWT")));
    }
}
```

Visit `http://localhost:8080/swagger-ui.html` once the app is running.
