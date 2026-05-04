# Stack Completeness Audit Results

**Date:** 2026-05-04
**Audited by:** 5 parallel subagents (one per stack + vibe agnosticism check)

---

## Summary Verdicts

| Stack | Verdict | Rules | Templates | Vibe | Examples | Critical Issues |
|---|---|---|---|---|---|---|
| `go-gin` | **STUB** | 2/4+ | 1/2 | 1/2 | 0/1 | No architecture/testing/style rules; REST-only; no gRPC |
| `java-spring` | **STUB** | 2/4+ | 1/2 | 1/2 | 0/1 | Stale Spring Boot 3.2.0; no Testcontainers pattern; no CQRS mention |
| `node-express` | **STUB** | 2/4+ | 1/2 | 1/2 | 0/1 | Template violates its own rule (console.log); no NestJS path; no error middleware |
| `devops-terraform` | **STUB** | 1/4+ | 0/2 | 0/2 | 0/1 | No templates dir; no vibe dir; no plan-out enforcement; Ansible/K8s not addressed |
| `python-datascience` | **PARTIAL** | 2/4+ | 1/2 | 1/2 | 0/1 | No model card template; no MLflow rule; no Spark/Databricks mention |
| `python-fastapi` | (not audited) | 9 rules | 12 templates | 7 vibe docs | yes | Reference implementation — the standard everything else must reach |

**All non-FastAPI stacks are STUB or PARTIAL. The gap between FastAPI and everything else is ~90%.**

---

## Audit Detail: go-gin

### Files found
```
rules/500-docker-go.mdc
rules/go-standards.mdc          ← no numeric prefix
templates/Dockerfile
templates/go-starter.md         ← 10-line main.go only
vibe/vibe_docker.md
```
No `examples/`.

### Top gaps
1. Missing rules: `000-workflow`, `100-architecture`, `200-testing`, `300-style`
2. No `phase-checklist.md` template
3. No `vibe_architecture.md` or `vibe_development_lifecycle.md`
4. No examples directory
5. `context.md` missing `Architecture Shape` field

### Microservice bias
- All templates assume Gin REST + PostgreSQL
- `vibe_docker.md` healthcheck uses HTTP `/health` — silently breaks for gRPC services
- `Dockerfile` hardcodes `cmd/server/main.go` — no CLI or gRPC entry point variant
- No mention of gRPC, protobuf, buf, connect-go anywhere

### Go-specific gaps
- No error wrapping (`fmt.Errorf("...: %w", err)`) rule
- No `context.Context` propagation example
- No table-driven test scaffold
- No graceful shutdown pattern (`os.Signal` + `Shutdown(ctx)`)
- No `golangci-lint` config template (`.golangci.yml`)
- No goroutine lifecycle / `errgroup` guidance
- No gRPC / protobuf rules at all

### Priority additions
| Priority | Item |
|---|---|
| HIGH | `rules/100-architecture.mdc` — Standard Go Layout for REST/gRPC/CLI; consumer-side interfaces; context propagation |
| HIGH | `rules/200-testing.mdc` — table-driven tests, testify, mockery/gomock, integration test build tags |
| HIGH | `examples/` — handler + service + repo + interface + table-driven test |
| HIGH | `templates/phase-checklist.md` |
| HIGH | `vibe/vibe_architecture.md` — REST vs gRPC vs CLI decision; layer responsibilities |
| MEDIUM | `rules/000-workflow.mdc` — feature branch, commit conventions, CI gate |
| MEDIUM | `rules/300-style.mdc` — naming, package naming, error string casing |
| MEDIUM | `vibe/vibe_development_lifecycle.md` |
| MEDIUM | Fix `go-standards.mdc` — add numeric prefix, split concerns |
| MEDIUM | Add error wrapping, graceful shutdown, `.golangci.yml` template |
| LOW | `rules/600-grpc.mdc` — protobuf, buf, interceptors, health check |
| LOW | "When Go over Java/Node" section in vibe |

---

## Audit Detail: java-spring

### Files found
```
rules/500-docker-java.mdc
rules/java-standards.mdc        ← no numeric prefix
templates/Dockerfile             ← broken layer caching (copies src before mvn dependency:go-offline)
templates/java-starter.md        ← pins Spring Boot 3.2.0 (stale), Java 17 (mismatches Docker 21)
vibe/vibe_docker.md
```
No `examples/`.

### Top gaps
1. Missing rules: `000-workflow`, `100-architecture`, `200-testing`, `300-style`
2. No `phase-checklist.md` template
3. No `vibe_architecture.md` or `vibe_development_lifecycle.md`
4. No examples directory
5. `context.md` missing `Architecture Shape` field

### Microservice bias
- Architecture defined as REST only: `web/` → `service/` → `repository/` → `model/`
- No mention of `@KafkaListener`, Spring Events, CQRS, or event-driven patterns
- `docker-compose` in vibe wires only `app + Postgres` — no Kafka/RabbitMQ variant
- `java-standards.mdc`: "Web Layer: `@RestController`. DTOs in, DTOs out." — REST-only framing

### Java-specific gaps
- No MapStruct vs manual mapping guidance (used at every Spring shop)
- No Checkstyle/Spotless config snippet (mentioned in context.md, never configured)
- No `@WebMvcTest` vs `@DataJpaTest` vs `@SpringBootTest` decision tree
- Testcontainers mentioned but no `@Testcontainers`/`@Container` setup pattern
- No `@Transactional` boundary rules (propagation, read-only, lazy-loading traps)
- No Jakarta Bean Validation (`@Valid`/`@Validated`) — dependency not even in starter pom
- Spring Boot 3.2.0 pinned — EOL; should be 3.3.x or 3.4.x
- Java 17 in pom vs Java 21 in Docker — mismatch
- No GraalVM Native Image / Spring AOT note

### Priority additions
| Priority | Item |
|---|---|
| HIGH | `rules/200-testing.mdc` — `@WebMvcTest`/`@DataJpaTest`/`@SpringBootTest` decision tree + Testcontainers pattern |
| HIGH | `templates/phase-checklist.md` |
| HIGH | `vibe/vibe_architecture.md` — layered vs hexagonal vs modular-monolith vs event-driven |
| HIGH | Fix version mismatch: Spring Boot → 3.3.x/3.4.x, Java → 21 everywhere |
| HIGH | `examples/` — CRUD resource with entity/DTO/service/controller/tests |
| MEDIUM | `rules/000-workflow.mdc` — TDD loop, PR checklist, commit conventions |
| MEDIUM | `rules/100-architecture.mdc` — package structure, DTO mapping (MapStruct), transaction boundaries, `@Valid` |
| MEDIUM | `rules/300-style.mdc` — Checkstyle config pointer, Spotless baseline, Lombok permitted annotations |
| MEDIUM | `vibe/vibe_development_lifecycle.md` |
| MEDIUM | Add MapStruct + spring-boot-starter-validation to starter pom |
| MEDIUM | Fix `Dockerfile` — add `mvn dependency:go-offline` layer caching |
| LOW | CQRS / event sourcing note in vibe_architecture.md |
| LOW | Spring Kafka / messaging starters as optional in starter pom |
| LOW | GraalVM Native Image note |

---

## Audit Detail: node-express

### Files found
```
rules/500-docker-node.mdc
rules/node-standards.mdc        ← no numeric prefix
templates/Dockerfile
templates/node-starter.md
templates/tsconfig.json
templates/src/app.ts
templates/src/server.ts         ← uses console.log, violating its own rule
vibe/vibe_docker.md
```
No `examples/`.

### Top gaps
1. Missing rules: `000-workflow`, `100-architecture`, `200-testing`, `300-style`
2. No `phase-checklist.md`
3. No `vibe_architecture.md` or `vibe_development_lifecycle.md`
4. No examples directory
5. `context.md` missing `Architecture Shape` field

### Microservice bias
- Architecture hard-coded as layered MVC REST — no mention of event-driven, queue workers, or serverless
- No message broker in docker-compose example
- NestJS mentioned only in Docker CMD comments — not as a first-class enterprise decision point

### Node-specific gaps (critical)
- `templates/src/server.ts` uses `console.log` — **directly contradicts its own rule** ("Use a logger, never console.log")
- No global async error middleware pattern in `app.ts`
- No NestJS vs Express decision tree anywhere
- No ORM alternatives (TypeORM, Drizzle) — Prisma only
- No Jest config, no test scaffold, no Supertest example
- No Zod middleware example (mentioned in rules but no code)
- No `package.json` template (no `scripts`, no dep list)
- `tsconfig.json` missing `resolveJsonModule`, `paths`, `declaration`

### Priority additions
| Priority | Item |
|---|---|
| HIGH | Fix `templates/src/server.ts` — replace `console.log` with pino/winston |
| HIGH | Add global error middleware to `templates/src/app.ts` |
| HIGH | `rules/000-workflow.mdc` |
| HIGH | `rules/100-architecture.mdc` — includes Express vs NestJS decision gate |
| HIGH | `rules/200-testing.mdc` — Jest unit + Supertest integration patterns |
| HIGH | `rules/300-style.mdc` — naming, import order, no-any |
| HIGH | `vibe/vibe_architecture.md` — layered MVC, Express vs NestJS, Prisma/TypeORM/Drizzle tradeoffs |
| HIGH | `vibe/vibe_development_lifecycle.md` |
| HIGH | `templates/phase-checklist.md` |
| MEDIUM | `examples/` — minimal CRUD resource with Zod, service, repo, Supertest test |
| MEDIUM | Zod middleware code template in `node-starter.md` |
| MEDIUM | `templates/package.json` with canonical scripts + dep list |
| MEDIUM | ORM alternatives in context.md and node-standards.mdc |
| LOW | Fix `Dockerfile` — add EXPOSE + HEALTHCHECK |
| LOW | NestJS modules/guards/interceptors reference section |

---

## Audit Detail: devops-terraform

### Files found
```
context.md
rules/devops-standards.mdc
```
**That is the entire stack. No `templates/`, no `vibe/`, no `examples/`.**

### Top gaps
1. Missing rules: `000-workflow`, `100-architecture`, `200-validate`, `300-style` (only 1 rules file total)
2. **`templates/` directory does not exist**
3. **`vibe/` directory does not exist**
4. **`examples/` directory does not exist**
5. `context.md` missing `Architecture Shape` field
6. No workspace/environment separation strategy defined

### Architecture bias
- Hard-coded AWS (S3 + DynamoDB) — no Azure/GCP remote state alternatives
- Conflates Terraform IaC with Python scripting automation in one rule file
- No workspace strategy (workspaces vs dir-per-env vs Terragrunt)

### DevOps-specific gaps (critical)
- No `terraform plan -out tfplan` enforcement (required by global CLAUDE.md, missing from stack)
- No module versioning rule
- No tflint/checkov/trivy CI gate configuration
- No drift detection mention
- No destroy protection rule (`prevent_destroy = true`)
- No pre-commit hooks (terraform_fmt, terraform_validate, tflint, checkov)
- **Ansible: zero mention — no ruling on whether in scope**
- **Kubernetes/Helm: zero mention — no ruling on whether in scope**
- **Pulumi: zero mention**
- **Terragrunt: zero mention**
- No terraform-docs / auto-documentation
- No Infracost / cost estimation

### Priority additions
| Priority | Item |
|---|---|
| HIGH | `templates/terraform-starter.md` — canonical module skeleton (main.tf, variables.tf, outputs.tf, versions.tf) |
| HIGH | `rules/000-workflow.mdc` — PR gate: plan attached, apply on merge, destroy flag |
| HIGH | `rules/100-architecture.mdc` — module layering, environment separation, module version pinning |
| HIGH | `rules/200-validate.mdc` — `plan -out tfplan`, tflint + checkov + trivy CI gate |
| HIGH | `templates/phase-checklist.md` — init → validate → plan → review → apply → verify → drift check |
| HIGH | Explicit Ansible/K8s scope ruling in context.md |
| MEDIUM | `rules/300-style.mdc` — HCL naming, tagging strategy, file organization |
| MEDIUM | `vibe/vibe_architecture.md` — immutable infra philosophy, cattle-not-pets, least-privilege |
| MEDIUM | `vibe/vibe_development_lifecycle.md` — Terraform workflow narrative, drift check cadence |
| MEDIUM | `examples/` — working VPC or S3+DynamoDB module in canonical structure |
| LOW | Terragrunt positioning note |
| LOW | Pulumi scope ruling |
| LOW | terraform-docs + pre-commit hooks |
| LOW | Infracost as optional CI step |

---

## Audit Detail: python-datascience

### Files found
```
rules/000-ds-workflow.mdc
rules/100-notebook-standards.mdc
templates/ds-starter.md
vibe/vibe_ds_workflow.md
```
No `examples/`. No model card template.

### Top gaps
1. Only 2 rules files (need 4+) — missing experiment-logging rule, data-versioning rule
2. Only 1 template — missing `model-card.md` template (rules mandate it, template doesn't exist)
3. Only 1 vibe doc — missing second doc
4. No `examples/` directory
5. `Architecture Shape` not as a discrete field

### DS-specific gaps
| Check | Status |
|---|---|
| MLflow | Listed as option alongside "plain CSV log" — not opinionated; no dedicated rule |
| Databricks / Spark | **Absent** — purely local/sklearn |
| DVC | **Not mentioned** — hash-only rule present but no tooling recommendation |
| Model card template | **Missing** — rules mandate it, no file exists |
| dbt / SQL analytics | **Absent** |
| Seed discipline | ✅ Well covered across rules, context.md, and templates |

### Priority additions
| Priority | Item |
|---|---|
| HIGH | `templates/model-card.md` — required by rules, does not exist |
| HIGH | `rules/200-mlflow.mdc` — opinionated: MLflow is the standard; plain CSV is a fallback only |
| MEDIUM | `rules/300-data-versioning.mdc` — DVC as the standard tool + hash-only fallback |
| MEDIUM | Second vibe doc (e.g., `vibe_experiment_philosophy.md`) |
| MEDIUM | `examples/` — end-to-end: EDA notebook → model → model card |
| LOW | Note on Spark/Databricks as out-of-scope for this stack (covered by `python-spark`) |

---

## Vibe Agnosticism Audit: vibe_development_lifecycle.md

**Finding:** `stacks/python-fastapi/vibe/vibe_development_lifecycle.md` is **~90% stack-agnostic**. It covers git workflow, branching strategy, commit conventions, PR format, quality gates — none of which are FastAPI-specific. The word "FastAPI" appears only in framing text (title, purpose statement, one Notes bullet).

**The document is misnamed.** It is a Python git workflow guide that lives in the wrong directory.

**Recommendation:**
1. **Extract** to `stacks/shared/vibe_git_workflow.md` — replace "FastAPI" with "Python" in 3 framing lines
2. **Replace** `python-fastapi/vibe/vibe_development_lifecycle.md` with a thin wrapper pointing to shared + adding FastAPI-specific concerns (OpenAPI versioning, router organization, schema migration discipline, Alembic workflow) — currently these are ABSENT from the existing doc
3. **Reference** the shared doc from `python-datascience`, `python-spark`, `python-dbt-snowflake` vibe directories — satisfies their minimum-2-docs requirement without duplication
4. **Create** a truly language-agnostic version at `stacks/shared/vibe_session_workflow.md` covering the session structure (start-session → work → next-session) with no language references — this becomes the base all stacks inherit

---

## New Stacks Needed (from research)

| Stack | Persona | Client fit | Priority |
|---|---|---|---|
| `go-grpc` | engineer | Intuit internal services | HIGH |
| `node-nestjs` | engineer | Salesforce, Travelers enterprise | HIGH |
| `devops-ansible` | devops | All clients using config management | HIGH |
| `devops-k8s-helm` | devops | Platform engineering / GitOps teams | HIGH |
| `python-spark` | data-scientist | Databricks/enterprise pipeline | HIGH |
| `python-dbt-snowflake` | data-scientist | Analytics engineering | HIGH |
| `java-quarkus` | engineer | Cloud-native Java (K8s/serverless) | MEDIUM |
| `java-spring-event` | engineer | Kafka/CQRS/Axon event-driven | MEDIUM |
| `r-tidyverse` | data-scientist | Travelers actuarial, financial services | MEDIUM |
| `python-mlops` | data-scientist | SageMaker/Vertex/Databricks deployment | MEDIUM |
| `devops-pulumi` | devops | Developer-first IaC teams | LOW |

---

## Implementation Order

### Phase 1 — Fix existing stacks (all STUB → PARTIAL or COMPLETE)
Priority order based on audit severity:
1. `devops-terraform` — most incomplete (0 templates, 0 vibe)
2. `go-gin` — missing 4 rules, no examples
3. `java-spring` — missing 4 rules, stale versions, no examples
4. `node-express` — template violates own rules, missing 4 rules
5. `python-datascience` — closest to complete; needs model card template + MLflow rule + examples

### Phase 2 — Extract shared vibe doc
- Create `stacks/shared/vibe_git_workflow.md` (Python-agnostic)
- Create `stacks/shared/vibe_session_workflow.md` (fully language-agnostic)
- Update python-fastapi to reference shared + add FastAPI-specific content

### Phase 3 — Add new stacks (parallel groups)
**Group A (HIGH, engineer persona):** `go-grpc`, `node-nestjs`
**Group B (HIGH, devops persona):** `devops-ansible`, `devops-k8s-helm`
**Group C (HIGH, data-scientist persona):** `python-spark`, `python-dbt-snowflake`
**Group D (MEDIUM):** `java-quarkus`, `r-tidyverse`, `python-mlops`

### Phase 4 — Make setup-stack persona-aware
- Engineer sees: go-gin, go-grpc, java-spring, java-quarkus, node-express, node-nestjs, python-fastapi
- DevOps sees: devops-terraform, devops-ansible, devops-k8s-helm, devops-pulumi
- Data Scientist sees: python-datascience, python-spark, python-dbt-snowflake, python-mlops, r-tidyverse
