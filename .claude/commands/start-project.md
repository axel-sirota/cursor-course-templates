---
description: "Scaffold the core domain: entities, interface contract, and implementation plan (adapts to active stack shape)"
---

# Start Project (Domain) Command

Initialize the *business logic* for a new feature or project. While `@setup-stack` handles the tech stack, this command handles the *domain model*.

## Inputs
- **Domain**: (e.g., "E-commerce", "Blog", "Task Manager")
- **Entities**: (Optional list, e.g., "Product, User, Order")

## Execution Flow

## Persona Detection (run first)

Read the active persona from context:
- Cursor: `.cursor/context.md` — look for `## Active Persona`
- Claude Code: `CLAUDE.md` — look for `## Active Persona`

If section missing or value is empty → treat as `engineer` (backwards compatible default).

Branch to the appropriate preamble below, then continue with the standard execution flow.

### Persona Preambles

**engineer:** Propose the domain design for the active stack shape:
- **Web API stacks**: data entities + REST endpoints + implementation phases
- **Pipeline stacks** (python-spark, python-mlops): data schemas + job stages + transformation plan
- **Analytics stacks** (python-dbt-snowflake): staging models + mart models + grain definition
- **IaC/Platform stacks** (devops-*): resource map + module inputs/outputs + role/chart structure

**designer:** Propose a component library inventory for the described UI: which components exist in the codebase, which need building, what tokens they require.

**pm:** Propose an initial user story map: key user roles, their goals, and an ordered list of epics with rough priority.

**data-scientist:** Propose a data pipeline design: input data sources, feature engineering steps, candidate model approaches, evaluation strategy.

---

**1. Context Analysis**
- Read `CLAUDE.md` to know the language/framework (e.g., Python FastAPI vs Node Express).

**2. Domain Modeling**
- Propose the **Data Model** (Entities/Tables) based on the Domain.
  - *Python*: Pydantic Models / SQLAlchemy.
  - *Node*: Prisma Schema.
  - *Java*: JPA Entities.
  - *dbt*: Staging model columns + mart grain definition.
  - *Terraform*: Variable definitions + resource block structure.
  - *Ansible*: Role defaults + variable contract (defaults/main.yml).
  - *Spark*: StructType schema definitions + Delta table structure.
  - *R*: Data frame column contract + function signatures.

**3. Interface Contract** (shape depends on active stack):
- **Web API**: REST endpoints (GET /resource, POST /resource)
- **Data Pipeline**: Job input/output schemas and stage interfaces
- **Analytics Model**: dbt model tree (staging → intermediate → mart)
- **IaC**: Module public interface (inputs, outputs, data sources)
- **Statistical Computing**: Quarto document sequence + Plumber API (if any)

**4. Implementation Plan**
- Generate a checklist to build this domain using the **Phase-Based Workflow** (Phase 0 -> Phase 1...).

## Usage
`/start-project "Library Management System"`
-> *Generates domain design and interface contract adapted to the active stack shape.*

