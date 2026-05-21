# Spring Boot Architecture Vibe

## Why Spring Boot
Spring Boot is the unmatched choice for enterprise Java web services. The ecosystem provides:
- **Spring Security** — authentication, authorization, OAuth2, JWT out of the box
- **Spring Data** — JPA, MongoDB, Redis, Elasticsearch repositories with near-zero boilerplate
- **Spring Batch** — robust batch processing with retry, skip, and partitioning
- **Spring Integration** — enterprise integration patterns (EIP) for complex messaging flows
- **Spring Cloud** — service discovery, circuit breakers, distributed config

Choose Spring Boot when you need a battle-tested, heavily tooled Java web service, especially with a large team, existing Java expertise, or complex enterprise integration requirements.

## When Quarkus Instead
Quarkus compiles to a GraalVM native image achieving sub-100ms startup and low memory footprint. Consider Quarkus when:
- Your team is already Java-fluent but needs Go-like startup times
- The service runs on Kubernetes and cold-start latency matters
- You're deploying to serverless (AWS Lambda, Google Cloud Run)
- Container image size and memory cost are primary constraints

If startup time is irrelevant (long-running services, batch jobs), Spring Boot's larger ecosystem usually wins.

## Architecture Shapes
All shapes follow the same layer discipline — only the entry point changes:

| Shape | Entry Point | Add |
|---|---|---|
| REST API (default) | `@RestController` | — |
| Event-driven | `@KafkaListener` | `spring-kafka` |
| Modular monolith | `@RestController` per module | `spring-modulith` |
| Batch processing | `@Job` / `@Step` | `spring-batch` |

The Controller → Service → Repository → Entity chain applies to all shapes. The event-driven shape replaces the HTTP controller with a message listener; the rest is identical.

## CQRS and Event Sourcing
For complex domains with high read/write asymmetry, consider CQRS (Command Query Responsibility Segregation):
- Write side: commands modify state, emit domain events
- Read side: projections build optimized read models from events

Axon Framework integrates natively with Spring Boot and provides full CQRS + event sourcing infrastructure.

Do not apply CQRS to simple CRUD applications — the overhead is not justified. Start with a layered REST API and extract CQRS patterns only when read/write scalability requirements demand it.

## Feature-Based Packaging
Package by feature (`users/`, `orders/`) not by layer (`controllers/`, `services/`). Benefits:
- Feature cohesion is visible in the IDE file tree
- Extracting a feature into a microservice means moving one package
- Onboarding developers navigate by domain concept, not by technical role

```
users/
    UserController.java
    UserService.java
    UserRepository.java
    User.java
    UserDto.java
    UserMapper.java
```

## MapStruct over Manual Mapping
MapStruct generates type-safe mappers at compile time with zero runtime overhead. Never write manual field-by-field mapping:

```java
// Forbidden — brittle, verbose, misses fields silently
UserDto dto = new UserDto(entity.getName(), entity.getEmail());

// Correct — MapStruct generates this automatically
@Mapper(componentModel = "spring")
public interface UserMapper {
    UserDto toDto(User entity);
    User toEntity(UserDto dto);
}
```

MapStruct errors at compile time if a field mapping is ambiguous, making refactors safe.
