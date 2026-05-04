# Research Artifact: Stack Expansion + Completeness Audit

**Cycles completed:** 6
**Searches run:** 30
**Date:** 2026-05-04

---

## Executive Summary

The current stack library covers 7 stacks but is severely under-specified for the client personas we serve:
- **Intuit**: needs `go-gin` deeply upgraded (gRPC/protobuf variant), `java-spring` (solid base but missing Quarkus variant), and a `go-grpc` new stack
- **Salesforce**: needs `java-spring` + `node-nestjs` (current is Express — too bare, enterprise clients need NestJS)
- **Travelers**: `node-nestjs` and `java-spring` (both already covered but need Kafka/event-driven vibes)
- **DevOps persona**: needs `devops-ansible` as a second stack alongside Terraform; also `devops-k8s-helm` for platform engineers; Pulumi as optional third
- **Data Scientist persona**: needs `python-spark` (PySpark/Databricks), `python-dbt-snowflake` (analytics engineer sub-stack), `r-tidyverse` (statistical computing), `python-mlops` (SageMaker/MLflow/Vertex)

**Critical finding:** All existing non-FastAPI stacks (`go-gin`, `java-spring`, `node-express`, `devops-terraform`) are **stub-level** — they have 1-2 rule files and a starter template but NO architecture guide (vibe), NO examples, NO lifecycle doc, NO phase-specific rules. `python-fastapi` has 9 rules, 12 templates, 7 vibe docs. Everything else has ~2 rules and 2 templates. Gap is ~90%.

**Critical finding 2:** All existing vibes and templates are **microservice/REST-API-first**. They assume: REST endpoints, Layered MVC, PostgreSQL, Docker, Swagger. This is wrong for:
- Go gRPC (not REST)
- Java CQRS/event-sourcing (not CRUD)
- Data scientist (not a service at all)
- DevOps (not an app)
- Analytics engineer (dbt models, not APIs)

---

## Key Findings Per Persona/Client

### Engineer Persona — Stacks Needed

| Stack | Client fit | Priority | Gap |
|---|---|---|---|
| `go-gin` (REST) | Intuit backend | HIGH | Rules thin, no vibe, no examples |
| `go-grpc` (new) | Intuit internal services | HIGH | Does not exist |
| `java-spring` (REST/CRUD) | Salesforce, Travelers | HIGH | Rules thin, no vibe, no examples |
| `java-quarkus` (new) | Cloud-native Java | MEDIUM | Does not exist |
| `java-spring-event` (new) | Kafka/CQRS/Axon pattern | MEDIUM | Does not exist |
| `node-nestjs` (new) | Salesforce, Travelers | HIGH | Current is express only — bare bones |
| `node-express` (REST) | Existing | MEDIUM | Rules thin, needs vibe |
| `python-fastapi` | Existing | LOW | Well-developed already |

### DevOps Persona — Stacks Needed

| Stack | Description | Priority | Gap |
|---|---|---|---|
| `devops-terraform` | Existing | HIGH | Has 1 rule. No vibe, no templates, no examples |
| `devops-ansible` (new) | Configuration management, idempotent playbooks, Molecule testing | HIGH | Does not exist |
| `devops-k8s-helm` (new) | Kubernetes + Helm + ArgoCD GitOps | HIGH | Does not exist |
| `devops-pulumi` (new) | TypeScript/Python IaC (developer-first orgs) | MEDIUM | Does not exist |

### Data Scientist Persona — Stacks Needed

| Stack | Description | Priority | Gap |
|---|---|---|---|
| `python-datascience` | Existing (sklearn/pandas/notebooks) | MEDIUM | Rules good, no examples, vibe too generic |
| `python-spark` (new) | PySpark + Databricks + Delta Lake + MLflow | HIGH | Does not exist |
| `python-dbt-snowflake` (new) | Analytics engineering: dbt + Snowflake/BigQuery | HIGH | Does not exist |
| `python-mlops` (new) | MLOps: SageMaker or Vertex or Databricks + model registry | MEDIUM | Does not exist |
| `r-tidyverse` (new) | Statistical computing: R + tidyverse + Plumber/Posit | MEDIUM | Does not exist |

---

## Completeness Standard (What "Complete" Means)

A stack pack is **complete** when it has ALL of:

### 1. `context.md` ✅ required
- Tech stack versions
- Architecture pattern (NOT assumed to be microservice — could be monolith, library, notebook, playbook, pipeline)
- Vibe & style decisions
- Key rules summary
- Active phase
- **NEW required field:** `## Architecture Shape` — one of: `REST API`, `gRPC Service`, `Event-Driven`, `CLI Tool`, `Library`, `Notebook`, `IaC Playbook`, `Data Pipeline`, `Analytics Model`

### 2. `rules/` — minimum 4 rules ✅ required
- `000-{stack}-workflow.mdc` — phase workflow (alwaysApply: true)
- `100-architecture.mdc` — structural rules (alwaysApply: true)
- `200-testing.mdc` — TDD / testing rules (alwaysApply: true)
- `300-style.mdc` — coding standards (alwaysApply: true)
- Optional: `500-docker.mdc`, `600-security.mdc`, `700-ci.mdc`

### 3. `templates/` — minimum 2 ✅ required
- `{stack}-starter.md` — hands-on scaffold/paste guide
- `phase-checklist.md` — phase gate checklist adapted to stack shape
- Optional: `openapi-template.yaml` (REST only), `proto-template.proto` (gRPC), `playbook-template.yml` (Ansible), `model-template.py` (DS)

### 4. `vibe/` — minimum 2 docs ✅ required
- `vibe_architecture.md` — WHY this stack shape; when to use monolith vs microservice vs notebook; the "spirit" of the tech
- `vibe_development_lifecycle.md` — git workflow, branching, session structure, handoff
- Optional: `vibe_database.md`, `vibe_docker.md`, `vibe_testing.md`, `vibe_kafka.md`

### 5. `examples/` — minimum 1 ✅ required
- At minimum: one reference implementation showing the correct pattern end-to-end
- Named `{stack}-reference/` or a single `complete-example.md`

---

## Vibe Agnosticism Problem (Critical Fix)

Current vibes assume:
- Architecture = microservice or REST API
- Database = PostgreSQL
- Deployment = Docker Compose
- Deliverable = running HTTP service

**Required change:** Vibes should open with an explicit `## When This Applies` section that states the architecture shape. Existing `vibe_development_lifecycle.md` in python-fastapi is 100% REST/service-specific — it talks about routes, endpoints, Swagger. It should be split into:

1. `vibe_development_lifecycle.md` — **language-agnostic** git/session workflow (no service-specific language)
2. `vibe_api_design.md` — REST-specific API design (only loaded for REST stacks)
3. `vibe_grpc_design.md` — gRPC-specific (only loaded for gRPC stacks)
4. `vibe_pipeline_design.md` — data pipeline design (DS stacks)
5. `vibe_iac_design.md` — infrastructure design (DevOps stacks)

The `vibe_development_lifecycle.md` in python-fastapi is re-usable across all stacks if stripped of FastAPI specifics. This is the **one canonical lifecycle doc** — it covers git flow, branch naming, session structure, commit discipline, PR format. Currently it's buried in python-fastapi only.

---

## New Stacks Specification

### `go-grpc` (new)
- Architecture Shape: gRPC Service
- Context: Go 1.22+, gRPC/protobuf, buf (proto linting), connect-go (alternative transport), PostgreSQL (sqlx), testify, golangci-lint
- Rules: grpc-workflow, proto-design, testing (table-driven + testcontainers), style (gofmt + golangci)
- Templates: proto-template.proto, service-starter.md, phase-checklist.md
- Vibe: vibe_architecture.md (when gRPC vs REST), vibe_grpc_design.md, vibe_development_lifecycle.md
- Examples: basic unary + streaming service example

### `node-nestjs` (new)
- Architecture Shape: REST API (modular, enterprise)
- Context: Node 20+, NestJS 10+, TypeScript strict, Prisma, Jest, ESLint
- Rules: nestjs-workflow, module-architecture, testing (unit + e2e), style
- Templates: module-starter.md, dto-template.md, phase-checklist.md
- Vibe: vibe_architecture.md (NestJS vs Express — when to choose), vibe_development_lifecycle.md
- Examples: feature-module with guard + interceptor + service + controller + e2e test

### `devops-ansible` (new)
- Architecture Shape: IaC Playbook
- Context: Ansible 9+, Molecule (Docker driver), ansible-lint, YAML
- Rules: ansible-workflow, idempotency-rules, molecule-testing, yaml-style
- Templates: role-template/, playbook-starter.md, molecule-config.md
- Vibe: vibe_architecture.md (Ansible vs Terraform — when each), vibe_iac_design.md
- Examples: complete role with molecule tests

### `devops-k8s-helm` (new)
- Architecture Shape: GitOps Platform
- Context: Kubernetes, Helm 3, ArgoCD, Kustomize optional, sealed-secrets or external-secrets
- Rules: gitops-workflow, helm-chart-standards, argocd-patterns, secrets-management
- Templates: chart-template/, argocd-app.yaml, phase-checklist.md
- Vibe: vibe_architecture.md (Helm vs Kustomize vs raw YAML), vibe_iac_design.md
- Examples: multi-env chart deployment with ArgoCD ApplicationSet

### `python-spark` (new)
- Architecture Shape: Data Pipeline
- Context: Python 3.11+, PySpark 3.5+, Databricks Runtime 14+, Delta Lake, MLflow, pytest + chispa (Spark testing)
- Rules: spark-workflow, delta-lake-standards, mlflow-logging, testing (chispa unit + integration)
- Templates: pipeline-starter.py, notebook-template.ipynb stub, phase-checklist.md
- Vibe: vibe_architecture.md (batch vs streaming vs lakehouse), vibe_pipeline_design.md
- Examples: end-to-end ELT pipeline: raw → bronze → silver → gold

### `python-dbt-snowflake` (new)
- Architecture Shape: Analytics Model
- Context: dbt Core 1.8+ or dbt Cloud, Snowflake / BigQuery, pytest-dbt, sqlfluff
- Rules: dbt-workflow, model-layering (staging/intermediate/mart), testing (schema tests + custom), style (sqlfluff)
- Templates: model-template.sql, schema.yml-template.yaml, phase-checklist.md
- Vibe: vibe_architecture.md (ELT philosophy, raw→staging→mart layers), vibe_pipeline_design.md
- Examples: full staging + mart model with tests and docs

### `r-tidyverse` (new)
- Architecture Shape: Statistical Computing / Notebook
- Context: R 4.4+, tidyverse, Quarto/R Markdown, testthat, lintr, Plumber (for API output)
- Rules: r-workflow, tidyverse-style (pipe operator, tidy data principles), testing (testthat), reproducibility
- Templates: analysis-starter.Rmd, plumber-api-starter.R, phase-checklist.md
- Vibe: vibe_architecture.md (R vs Python — when R wins), vibe_pipeline_design.md
- Examples: EDA → model → Plumber API or Shiny dashboard

---

## Antithesis (What Could Go Wrong)

1. **Too many stacks → context bloat**: 15+ stacks means students drown in options. Mitigation: `setup-stack` presents only persona-relevant stacks (engineer sees Go/Java/Node; DS sees Python/R/Spark; DevOps sees Terraform/Ansible/K8s).

2. **Vibe docs become stale**: If we write too-specific vibes (e.g., "use Panache.NextEntity()") they break when frameworks update. Mitigation: Vibes describe patterns and rationale, not API calls. API specifics live only in rules.

3. **R stack is low-value for most clients**: R is primarily actuarial/statistical, not mainstream engineering. Travelers could use it (insurance math), but Intuit/Salesforce likely won't. Mitigation: Mark as optional, only present for data-scientist persona.

4. **Quarkus vs Spring Boot fragmentation**: Having both `java-spring` and `java-quarkus` creates choice paralysis. Mitigation: One stack (`java-spring`) is default; Quarkus is a variant only surfaced when `setup-stack` detects GraalVM/serverless context.

---

## Proposed Plan

### Phase 1: Fix existing stacks (all have gaps)
1. `go-gin`: Add 3 more rules (architecture, testing, style) + vibe (architecture + lifecycle) + examples
2. `java-spring`: Add rules (architecture, testing, checkstyle) + vibe + examples
3. `node-express`: Add rules (architecture, testing, style) + vibe + examples
4. `devops-terraform`: Add 3 rules (module-design, testing, security) + vibe (2 docs) + templates (2) + examples
5. `python-datascience`: Add examples; fix vibe to be agnostic (notebook-first, not service-first)

### Phase 2: Add high-priority new stacks (parallel)
- `go-grpc` — Intuit internal services
- `node-nestjs` — Salesforce/Travelers enterprise Node
- `devops-ansible` — config management companion to Terraform
- `devops-k8s-helm` — platform engineering / GitOps

### Phase 3: Add DS sub-stacks (parallel)
- `python-spark` — Databricks/enterprise pipeline
- `python-dbt-snowflake` — analytics engineering
- `r-tidyverse` — statistical/actuarial (Travelers)

### Phase 4: Universalize vibe lifecycle
- Extract `vibe_development_lifecycle.md` as a shared canonical doc (git flow, session structure, PRs)
- Move to `stacks/shared/` or reference from each stack's vibe/
- All stack-specific vibes link to it instead of duplicating

### Phase 5: Make `setup-stack` persona-aware
- DevOps persona: shows only `devops-*` stacks
- Data Scientist: shows only `python-*` and `r-*` stacks
- Engineer: shows `go-*`, `java-*`, `node-*`, `python-fastapi`

---

## Sources

- [Intuit Technology Stack](https://stackshare.io/intuit/intuit)
- [Salesforce Tech Stack](https://himalayas.app/companies/salesforce/tech-stack)
- [Travelers Node/Java Jobs](https://careers.travelers.com/job/22647159/software-engineer-i-aws-node-atlanta-ga/)
- [Go gRPC microservices patterns](https://dev.to/nikl/building-production-grade-microservices-with-go-and-grpc-a-step-by-step-developer-guide-with-example-2839)
- [Go project structure 2025](https://www.glukhov.org/post/2025/12/go-project-structure/)
- [Spring Boot vs Quarkus vs Micronaut 2026](https://www.javacodegeeks.com/2025/12/spring-boot-vs-quarkus-vs-micronaut-the-ultimate-2026-showdown.html)
- [NestJS enterprise architecture 2026](https://encore.dev/articles/nestjs-project-structure-best-practices)
- [Terraform vs Pulumi vs CDK 2026](https://sanj.dev/post/terraform-pulumi-aws-cdk-2025-decision-framework)
- [Ansible + Molecule testing](https://yrkan.com/blog/ansible-testing-with-molecule/)
- [Helm + ArgoCD GitOps patterns](https://medium.com/@anip.shah1/advanced-gitops-patterns-with-argocd-helm-progressive-delivery-342a8a2758f9)
- [Databricks ML stack 2026](https://wishtreetech.com/blogs/cloud-engineering/databricks-on-aws-the-ultimate-stack-for-ai-driven-analytics-in-2026/)
- [SageMaker vs Databricks vs Vertex AI](https://startupik.com/sagemaker-vs-databricks-vs-vertex-ai-which-ml-platform-is-better/)
- [Modern Data Stack 2025 winners](https://medium.com/@reliabledataengineering/the-modern-data-stack-in-2025-what-actually-won-708c59176b32)
- [dbt skills demand 2025](https://www.getdbt.com/blog/data-engineer-skills-2025)
- [Scala/Spark Delta Lake 2025](https://datalakehousehub.com/blog/2025-09-2026-guide-to-data-lakehouses/)
- [R in enterprise 2026](https://posit.co/blog/building-data-science-infrastructure-at-an-enterprise-level-with-rstudio-and-procogia)
- [Java Spring Boot Cursor rules](https://github.com/jabrena/cursor-rules-spring-boot)
- [AI coding completeness checklist](https://stackoverflow.blog/2026/03/26/coding-guidelines-for-ai-agents-and-people-too/)
- [Vibe coding structured workflow](https://dev.to/wasp/a-structured-workflow-for-vibe-coding-full-stack-apps-352l)
- [Intuit Go+Java job postings](https://jobs.intuit.com/job/mountain-view/principal-software-engineer-trust-and-safety/27595/92059338864)
