---
description: Scaffold business domain features (Models, API, Service)
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

**engineer:** Propose data entities, REST API endpoints, and implementation phases for the described domain.

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

**3. API Surface**
- Propose the **REST API** endpoints.
  - `GET /products`, `POST /orders`.

**4. Implementation Plan**
- Generate a checklist to build this domain using the **Phase-Based Workflow** (Phase 0 -> Phase 1...).

## Usage
`/start-project "Library Management System"`
-> *Generates Book/Author models and API plan in the active language.*

