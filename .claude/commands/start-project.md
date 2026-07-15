---
description: Scaffold the core domain (entities, interface contract, plan) — adapts to active stack shape
---

# Start Project (Domain) Command

Initialize the *business logic* for a new feature or project. While `/setup-stack` handles the tech stack, this command handles the *domain* — whatever "domain" means for the active stack's shape (data model + API for a web service, resources + variables for infra, commands + flags for a CLI, etc.).

## Inputs
- **Domain**: (e.g., "E-commerce", "Blog", "Task Manager")
- **Entities**: (Optional list, e.g., "Product, User, Order")

## Execution Flow

**1. Context Analysis**
- Read `CLAUDE.md` to determine the **Active Stack** and its **Architecture Shape** (web-service, infra-as-code, library, CLI, ui-only, etc.).
- **Condition**: If Architecture Shape is unset, stop and point the user to `/setup-stack`.

**2. Domain Surface (shape-aware)**
Propose the domain's primary artifacts based on Architecture Shape:

- **Web Service** (e.g., python-fastapi, node-express, java-spring, go-gin):
  - **Data Model**: Entities/tables, using the ORM/schema convention documented by the active stack's rules (see `.claude/rules/`).
  - **API Surface**: REST/RPC routes or methods.
    - Example: `GET /products`, `POST /orders`.

- **Infra-as-Code** (e.g., devops-terraform):
  - **Resource Model**: Terraform resources, variables, outputs, and module boundaries — instead of a Data Model.
  - **Public Contract**: The module's input variables and outputs — instead of an API Surface.

- **Library**:
  - **Public API Surface**: Exported types, functions, and classes.
  - No Data Model step unless the library itself models data.

- **CLI**:
  - **Command Tree**: Commands, subcommands, flags, and config schema — instead of REST endpoints.

- **UI-Only**:
  - **Component/View Model**: Components, view state, and data shape.
  - **User-Facing Surface**: Routes/screens — instead of REST endpoints.

- **Blank / Unrecognized Shape**:
  - Ask the user directly what artifacts constitute "the domain" for this project before proposing anything. Do not default to REST+DB.

**3. Implementation Plan**
- Generate a checklist to build this domain's artifacts (as scoped in step 2) using the **Phase-Based Workflow** (Phase 0 -> Phase 1...).

## Usage
`/start-project "Library Management System"`
-> *Generates the domain's artifacts (models/resources/commands/components as appropriate) and an implementation plan for the active stack.*
