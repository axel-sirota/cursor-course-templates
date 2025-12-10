---
description: Execute Phase 0 (Architecture & Skeleton) using active stack context
---

# Architect Phase Command

Initiates **Phase 0** of the development lifecycle. This command guides the Agent to design the API surface, verify the "shape" of the application, and mock the skeleton before implementation.

This command works in **two modes**: Design Mode (AI designs everything) or Plan Extraction Mode (use existing plan).

## Execution Flow

**0. Check for Plan Document**
- **Action**: Check if user provided a plan document
- **Look for**:
  - User explicitly provided file path: `@architect plan.md` or `@architect path/to/requirements.md`
  - User pasted plan content in the message
  - Common plan files in project: `plan.md`, `requirements.md`, `PRD.md`, `design.md`
  - Plan files in `plan/` directory: `plan/requirements.md`, `plan/design.md`

- **Decision**:
  - If plan found → **Plan Extraction Mode** (go to step 1A)
  - If no plan → **Design Mode** (go to step 1B)

---

### Plan Extraction Mode (When Plan Exists)

**1A. Context Loading**
- Read `.cursor/context.md` to identify the **Active Stack**
- Read the provided plan document
- Read `.cursor/rules/*.mdc` to understand the **Stack Standards**

**2A. Extract Requirements from Plan**
- **Goal**: Use the plan AS-IS, do not re-design or question architectural decisions
- **Extract**:
  - **Technical Requirements**: What features/endpoints are specified?
  - **API Surface**: Which routes, methods, request/response formats are defined?
  - **Data Model**: Which entities, relationships, fields are mentioned?
  - **Architecture**: What architectural decisions are already specified? (e.g., "use microservices", "layered architecture")
  - **Tech Stack Specifics**: Any specified libraries, frameworks, patterns?

- **Critical Rule**:
  - **Trust the plan** - if the plan says "use REST API", use REST API
  - **Do NOT suggest alternatives** - if plan says "MongoDB", don't suggest PostgreSQL
  - **Do NOT re-design** - if plan has architecture diagram, follow it exactly

- **If Unclear**:
  - Ask user for clarification: "The plan mentions 'user authentication' but doesn't specify OAuth vs JWT. Which should I use?"
  - Do NOT assume or make decisions that contradict the plan

**3A. Verify Compatibility with Active Stack**
- **Check**: Does the plan's tech stack match `.cursor/context.md`?
  - Example: Plan says "Node.js" but context.md says "Python FastAPI"

- **If Mismatch**:
  - Warn user: "Your plan specifies Node.js but active stack is Python FastAPI. Would you like me to:"
    - Option 1: "Update context to Node.js (run @setup-stack)"
    - Option 2: "Adapt plan to Python FastAPI"
  - Wait for user decision

- **If Match**:
  - Proceed with plan extraction

**4A. Generate Phase Breakdown**
- **Goal**: Break the plan into implementation phases
- **Action**: Based on plan's features, create phase structure:
  - **Phase 0**: Skeleton (mock all endpoints from plan)
  - **Phase 1+**: Implement each feature group from plan

- **Example**:
  ```
  Plan mentions: User Auth, Product Catalog, Shopping Cart, Checkout

  Phases:
  - Phase 0: Skeleton (mock all 4 feature areas)
  - Phase 1: User Auth (as specified in plan)
  - Phase 2: Product Catalog (as specified in plan)
  - Phase 3: Shopping Cart (as specified in plan)
  - Phase 4: Checkout (as specified in plan)
  ```

**5A. Generate Session Plans**
- **Goal**: Create detailed session markdown files in `plan/sessions/`
- **Action**: For each phase, create session file based on plan's specifications

- **Example Session File** (`plan/sessions/session-1-phase-0.md`):
  ```markdown
  # Session 1: Phase 0 - Skeleton

  ## Goal
  Build walking skeleton based on [plan.md] specifications

  ## Requirements (from plan)
  - [Extract exact requirements from plan]
  - [List all endpoints mentioned in plan]
  - [List all data models mentioned in plan]

  ## Implementation
  - Scaffold directory structure per active stack
  - Create mock endpoints for:
    - [Endpoint 1 from plan]
    - [Endpoint 2 from plan]
  - Return hardcoded 200 OK responses

  ## Verification
  - Run app, verify all endpoints respond
  - Check against plan: all specified endpoints exist
  ```

**6A. Skeleton Implementation**
- **Goal**: Build the walking skeleton based on plan specifications
- **Action**:
  - Scaffold directory structure (per active stack)
  - Create entrypoint (e.g., `main.py`, `server.ts`)
  - Create **mock endpoints** for ALL features mentioned in plan
  - Mock responses match plan's specified response formats

**7A. Final Output**
- Inform user:
  ```
  ✅ Plan extracted from [plan.md]
  ✅ [N] phases identified
  ✅ [M] session plans created in plan/sessions/
  ✅ Skeleton implemented based on plan specifications

  Next: Run @start-session to begin implementation
  ```

---

### Design Mode (No Plan - AI Designs Everything)

**1B. Context Loading**
- Read `.cursor/context.md` to identify the **Active Stack**
- Read `METHODOLOGY.md` to understand the "Phase 0" concept
- Read `.cursor/rules/*.mdc` to understand the **Stack Standards**

**2B. Design Verification**
- **Goal**: Define the API/Interface Contract (AI designs this)
- **Action**:
  - If **Web API**: Design the OpenAPI spec or Routes
  - If **CLI**: Design the Command Arguments
  - If **Terraform**: Design the Root Module inputs/outputs
  - If **Library**: Design the Public API surface

- **Constraint**: Ensure the design matches the **Architecture Pattern** defined in `.cursor/context.md` (e.g., "Layered Monolith", "Modular")

- **Example (Web API)**:
  ```
  User: @architect "Build a blog API"

  AI Designs:
  - POST /posts (create post)
  - GET /posts (list posts)
  - GET /posts/{id} (get single post)
  - PUT /posts/{id} (update post)
  - DELETE /posts/{id} (delete post)
  - POST /posts/{id}/comments (add comment)
  - GET /posts/{id}/comments (list comments)
  ```

**3B. Skeleton Implementation**
- **Goal**: Build the "Walking Skeleton" (Input -> Controller -> Service -> Mock -> Output)
- **Action**:
  - Scaffold the directory structure (if missing)
  - Create the Entrypoint (e.g., `main.py`, `server.ts`)
  - Create **Mock Endpoints** (return hardcoded 200 OK)
  - **Verify**: Can we run the app? Does it respond?

**4B. Planning**
- **Goal**: Break down the implementation into Sessions
- **Action**: Create a `plan/` directory (if relevant)
- **Output**: A list of "Implementation Sessions" (e.g., "Session 1: User Auth", "Session 2: Products")

- **Create Session Files**:
  ```
  plan/
  ├── sessions/
  │   ├── session-1-phase-0.md   # Skeleton
  │   ├── session-2-phase-1.md   # First feature
  │   └── session-3-phase-1.md   # Second feature
  ```

**5B. Final Output**
- Inform user:
  ```
  ✅ API designed with [N] endpoints
  ✅ [M] phases identified
  ✅ Session plans created in plan/sessions/
  ✅ Skeleton implemented

  Next: Run @start-session to begin implementation
  ```

---

## Usage Examples

### Example 1: With Plan (Plan Extraction Mode)
```
@architect plan.md
```
or
```
@architect path/to/requirements.md
```
→ Reads plan → Extracts requirements → Breaks into phases → Builds skeleton based on plan

### Example 2: Without Plan (Design Mode)
```
@architect "Build a task management API"
```
→ AI designs API → Creates phases → Builds skeleton

### Example 3: With Pasted Plan
```
@architect

Here's the plan:
- User authentication with JWT
- CRUD operations for tasks
- Task assignment to users
- Due date tracking
```
→ Extracts from pasted plan → Breaks into phases → Builds skeleton

---

## Key Differences Between Modes

| Aspect | Plan Extraction Mode | Design Mode |
|--------|---------------------|-------------|
| **Input** | Plan document provided | User description only |
| **AI Role** | Extract & organize | Design & propose |
| **Architecture** | Use plan's decisions | AI proposes architecture |
| **Tech Stack** | Follow plan's choices | Use active stack |
| **Flexibility** | Trust the plan | AI has freedom to design |
| **Clarifications** | Ask if plan is unclear | Make reasonable assumptions |

---

## Notes

- **Plan Extraction Mode is faster**: No design phase needed, just extract and organize
- **Plan trumps AI suggestions**: If plan specifies something, use it exactly
- **Ask when unclear**: Better to ask user than assume wrong approach
- **Verify stack compatibility**: Warn if plan's tech stack differs from active context
