---
description: Execute Phase 0 (Architecture & Skeleton) using active stack context
---

# Architect Phase Command

Initiates **Phase 0** of the development lifecycle. This command guides the Agent to design the API surface, verify the "shape" of the application, and mock the skeleton before implementation.

## Execution Flow

**1. Context Loading**
- Read `.cursor/context.md` to identify the **Active Stack**.
- Read `METHODOLOGY.md` to understand the "Phase 0" concept.
- Read `.cursor/rules/*.mdc` to understand the **Stack Standards**.

**2. Design Verification**
- **Goal**: Define the API/Interface Contract.
- **Action**:
  - If **Web API**: Design the OpenAPI spec or Routes.
  - If **CLI**: Design the Command Arguments.
  - If **Terraform**: Design the Root Module inputs/outputs.
- **Constraint**: Ensure the design matches the **Architecture Pattern** defined in `context.md` (e.g., "Layered Monolith", "Modular").

**3. Skeleton Implementation**
- **Goal**: Build the "Walking Skeleton" (Input -> Controller -> Service -> Mock -> Output).
- **Action**:
  - Scaffold the directory structure (if missing).
  - Create the Entrypoint (e.g., `main.py`, `server.ts`).
  - Create **Mock Endpoints** (return hardcoded 200 OK).
  - **Verify**: Can we run the app? Does it respond?

**4. Planning**
- **Goal**: Break down the implementation into Sessions.
- **Action**: Create a `plan/` directory (if relevant).
- **Output**: A list of "Implementation Sessions" (e.g., "Session 1: User Auth", "Session 2: Products").

## Usage
`@architect "Design the User Profile feature"`
-> *Reads Python Context -> Updates OpenAPI -> Mocks User Routes -> Plans Sessions.*
