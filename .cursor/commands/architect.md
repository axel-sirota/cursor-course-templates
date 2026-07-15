---
description: Execute Phase 0 (Architecture & Skeleton) using active stack context
---

# Architect Phase Command

Initiates **Phase 0** of the development lifecycle. This command guides the Agent to design the interface surface (API routes, CLI commands, Terraform module I/O, library exports, UI screens, etc.), verify the "shape" of the project, and mock the skeleton before implementation.

This command works in **two modes**: Design Mode (AI designs everything) or Plan Extraction Mode (use existing plan).

## Stack Shape Reference

Every step below that mentions an entrypoint, mock/skeleton behavior, or verification method MUST branch on the active stack's declared **shape**, exactly as follows. Determine the shape from `.cursor/context.md` (the Active Stack / Architecture Shape). Do not default to Web API assumptions for a non-Web-API stack.

| Shape | Entrypoint example | Skeleton / mock behavior | Verification method |
|-------|--------------------|---------------------------|----------------------|
| **Web API** | `main.py`, `server.ts`, or stack's documented entrypoint | Mock routes return hardcoded 200 OK with the planned response shape | Start the server, hit each mocked route, confirm response |
| **CLI** | Stack's documented CLI entrypoint (e.g. `cli.py`, `cmd/root.go`) | Mock each command/subcommand to accept its planned args and print a placeholder result | Run each command with `--help` and with mock args; confirm exit code 0 and expected stdout shape |
| **Terraform / IaC** | `main.tf` (root module) | Mock/placeholder variables and resource stubs wired per the planned module inputs/outputs | `terraform init && terraform validate && terraform plan` succeeds with mock/placeholder vars |
| **Library** | The package's public export/`__init__` (or stack's documented package entrypoint) | Stub each public function/class to accept planned args and return a placeholder value | Import the package, call each public function/class with mock args, confirm no errors — or run a smoke test file |
| **UI-only** | Stack's documented app entrypoint (e.g. `index.html`, `App.tsx`) | Stub components/pages per the planned screens, rendering placeholder content | Build succeeds and each component renders without runtime error |
| **Other / not listed above** | Ask the user what the entrypoint convention is, or infer from `.cursor/rules/*.mdc` | Stub the planned unit of work per stack rules | Ask the user for (or infer from stack rules) the appropriate run/validate/test command that proves the skeleton executes |

This table is the single source of truth for entrypoint/mock/verification language in this command — every step below references it instead of restating Web-API-specific text.

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

**5A. Write Phase/Session State (MANDATORY)**
- **Goal**: Persist the phase breakdown as durable, machine-readable state
- **Requirement**: Write `plan/PHASES.md` using the **exact schema** below. This file MUST exist on disk before this command reports success — do not proceed to step 6A/7A until the Write has been performed and verified by re-reading the file. This is the single shared state file read/written by `@architect`, `@start-session`, and `@next-session`. Do not create `plan/sessions/*.md` files or any alternate format.

- **Exact schema** (fill in brackets from the plan; use the Stack Shape Reference table above for the "Verify skeleton" wording):
  ```markdown
  # Project Phases

  current_phase: 0
  current_status: not_started   # not_started | in_progress | blocked | complete

  ## Phase 0: Skeleton
  - Status: not_started
  - Goal: Build walking skeleton based on [plan.md] specifications
  - Done:
    - (none yet)
  - Pending:
    - Scaffold directory structure per active stack
    - Build walking skeleton for: [feature/endpoint/command/module 1 from plan], [feature/endpoint/command/module 2 from plan], ...
    - Verify skeleton ([per-stack verification method from Stack Shape Reference])

  ## Phase 1: [Feature group 1 from plan]
  - Status: not_started
  - Goal: [one-line goal, as specified in plan]
  - Done:
    - (none yet)
  - Pending:
    - [Implementation item from plan]

  ## Phase 2: [Feature group 2 from plan]
  - Status: not_started
  - Goal: [one-line goal, as specified in plan]
  - Done:
    - (none yet)
  - Pending:
    - [Implementation item from plan]
  ```
- Add one `## Phase N: ...` section per phase identified in step 4A.

**6A. Skeleton Implementation**
- **Goal**: Build the walking skeleton based on plan specifications
- **Action**:
  - Scaffold directory structure (per active stack)
  - Create entrypoint per the active stack's shape (see Stack Shape Reference table above)
  - Create **mock/stub units** for ALL features mentioned in plan, per the "Skeleton / mock behavior" column for the active shape
  - Mock outputs match plan's specified formats
  - Run the verification method for the active shape (see Stack Shape Reference table above) and confirm it passes
  - Update `plan/PHASES.md`: mark Phase 0's "Verify skeleton" and scaffolding items as Done, set Phase 0 `Status: complete`, set `current_phase: 1` and Phase 1 `Status: in_progress` at the top of the file

**7A. Final Output**
- Inform user:
  ```
  ✅ Plan extracted from [plan.md]
  ✅ [N] phases identified
  ✅ plan/PHASES.md created (current_phase: 1)
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

- **Example (CLI)**:
  ```
  User: @architect "Build a task CLI"

  AI Designs:
  - task add <title> [--due DATE]
  - task list [--status STATUS]
  - task complete <id>
  - task delete <id>
  ```

- **Example (Terraform)**:
  ```
  User: @architect "Provision an S3-backed static site module"

  AI Designs:
  - Inputs: bucket_name, region, index_document, tags
  - Outputs: bucket_arn, website_endpoint
  - Resources: aws_s3_bucket, aws_s3_bucket_website_configuration, aws_s3_bucket_policy
  ```

- **Example (Library)**:
  ```
  User: @architect "Build a rate-limiter library"

  AI Designs:
  - RateLimiter(max_calls, period) constructor
  - .allow() -> bool
  - .reset() -> None
  - .remaining -> int (property)
  ```

**3B. Skeleton Implementation**
- **Goal**: Build the "Walking Skeleton" (Input -> Controller/Handler -> Service -> Mock -> Output) for the active stack's shape
- **Action**: Using the Stack Shape Reference table above:
  - Scaffold the directory structure (if missing)
  - Create the entrypoint per the active shape
  - Create the mock/stub units per the active shape's "Skeleton / mock behavior"
  - Run the active shape's verification method and confirm it passes

**4B. Planning**
- **Goal**: Break down the implementation into Phases/Sessions
- **Action**: Create a `plan/` directory (if missing)
- **Output**: A list of "Implementation Phases" (e.g., "Phase 1: User Auth", "Phase 2: Products")

**5B. Write Phase/Session State (MANDATORY)**
- **Goal**: Persist the phase breakdown as durable, machine-readable state
- **Requirement**: Write `plan/PHASES.md` using the **exact schema** below. This file MUST exist on disk before this command reports success — do not proceed to step 6B until the Write has been performed and verified by re-reading the file. This is the single shared state file read/written by `@architect`, `@start-session`, and `@next-session`. Do not create `plan/sessions/*.md` files or any alternate format.

  ```markdown
  # Project Phases

  current_phase: 0
  current_status: not_started   # not_started | in_progress | blocked | complete

  ## Phase 0: Skeleton
  - Status: not_started
  - Goal: <one-line goal>
  - Done:
    - (none yet)
  - Pending:
    - Scaffold directory structure per active stack
    - Build walking skeleton per active stack shape
    - Verify skeleton ([per-stack verification method from Stack Shape Reference])

  ## Phase 1: <name>
  - Status: not_started
  - Goal: <one-line goal>
  - Done:
    - (none yet)
  - Pending:
    - <item>
  ```
- Add one `## Phase N: ...` section per phase identified in step 4B.
- After completing the skeleton in step 3B, update `plan/PHASES.md`: mark Phase 0's scaffolding/skeleton/verify items as Done, set Phase 0 `Status: complete`, set `current_phase: 1` and Phase 1 `Status: in_progress` at the top of the file.

**6B. Final Output**
- Inform user:
  ```
  ✅ [Interface/API/CLI/Module] designed with [N] units
  ✅ [M] phases identified
  ✅ plan/PHASES.md created (current_phase: 1)
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
- **Stack-shape-aware, not Web-API-only**: Entrypoint, mock behavior, and verification always follow the Stack Shape Reference table for the active stack (Web API / CLI / Terraform / Library / UI / Other) — never assume a running server or HTTP responses for non-Web-API stacks
- **`plan/PHASES.md` is the only phase/session state file**: `@architect` always creates or updates it before reporting success; `@start-session` reads it to report the current phase; `@next-session` writes progress back into it. No other file or format (e.g. `plan/sessions/*.md`) is used for this purpose
