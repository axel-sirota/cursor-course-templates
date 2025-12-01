---
description: Scaffold business domain features (Models, API, Service)
---

# Start Project (Domain) Command

Initialize the *business logic* for a new feature or project. While `@setup-stack` handles the tech stack, this command handles the *domain model*.

## Inputs
- **Domain**: (e.g., "E-commerce", "Blog", "Task Manager")
- **Entities**: (Optional list, e.g., "Product, User, Order")

## Execution Flow

**1. Context Analysis**
- Read `.cursor/context.md` to know the language/framework (e.g., Python FastAPI vs Node Express).

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
`@start-project "Library Management System"`
-> *Generates Book/Author models and API plan in the active language.*

