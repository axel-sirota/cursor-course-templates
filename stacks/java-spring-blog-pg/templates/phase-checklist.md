# Phase Checklist — java-spring-blog-pg

## Phase 0 — Skeleton
- [ ] `pom.xml` with Spring Boot 3.4.x, Java 17, web + validation + data-jpa + flyway + postgresql + lombok + mapstruct + testcontainers
- [ ] `BlogApplication.java` (only `main`, nothing else)
- [ ] `application.yml` (profiles: default, test, docker)
- [ ] `shared/`: `ErrorResponse`, `NotFoundException`, `GlobalExceptionHandler`
- [ ] `db/migration/V1__init.sql` (empty schema bootstrap)
- [ ] `Dockerfile` + `docker-compose.yml` + `.env.example`
- [ ] `mvn verify` green with zero features

## Phase 1 — First Feature (`posts/`)
- [ ] `PostDto` record + validation
- [ ] `Post` entity (`@Entity`, mutable, protected no-arg ctor)
- [ ] `PostRepository` (domain interface, package-private)
- [ ] `JpaPostRepository extends JpaRepository<Post, UUID>, PostRepository` (package-private)
- [ ] `PostMapper` (`@Mapper(componentModel = "spring")`)
- [ ] `PostService` with `@Transactional` write methods, `@Transactional(readOnly = true)` reads
- [ ] `PostController` at `/api/posts` (GET list, POST create, GET id, PUT id, DELETE id)
- [ ] `V2__posts.sql` migration
- [ ] `PostControllerTest` (`@WebMvcTest`)
- [ ] `PostServiceTest` (plain Mockito)
- [ ] `JpaPostRepositoryTest` (`@DataJpaTest` + Testcontainers)
- [ ] `mvn verify` green

## Phase 2 — Second Feature (`comments/`)
- [ ] Repeat the Phase 1 shape for comments
- [ ] FK to `posts.id` in `V3__comments.sql`
- [ ] Cascade rules decided and documented

## Phase 3 — Polish
- [ ] Pagination on list endpoints (`Pageable` at the controller, translated to domain in the repo)
- [ ] OpenAPI via `springdoc-openapi-starter-webmvc-ui`
- [ ] Container reuse for Testcontainers (singleton pattern)
- [ ] CI: GitHub Actions running `mvn verify` on PRs
