# Core Methodology: Agentic SDLC

This document defines the **language-agnostic principles** behind the AI-Assisted Development Template in Cursor IDE. These principles apply to every persona (engineer, pm, designer, data-scientist, accountant), and whether you are writing Python, Go, TypeScript, Java, building a PRD, or closing a month.

---

## Core Principles

### 1. Phase-Based Development
Software is built in distinct layers, not vertical slices.

- **Phase 0 (Skeleton)**: Build the structure first. Mock every endpoint. Verify the "shape" of the API before writing logic.
- **Phase 1+ (Implementation)**: Implement one endpoint at a time.
- **Why?**: Prevents getting stuck in implementation details before the architecture is proven.
- **Other roles**: the "endpoint" is whatever the Architecture Shape names: a PRD section (pm), a token or component (designer), a notebook or pipeline step (data-scientist), a workpaper step (accountant). Phase 0 stubs them all.

### 2. Test-Driven Development (TDD)
Tests are not "quality assurance"; they are **design tools**.

- **The Rule**: You cannot write implementation code until a test fails.
- **The Flow**: Red (Write Test) → Green (Make it Pass) → Refactor (Clean up).
- **AI Role**: The AI is excellent at writing tests if you give it the skeleton (Phase 0).
- **Per role**: "test" means the check that fits the role: Hurl acceptance tests plus unit tests (engineer), INVEST and Given/When/Then checks (pm), token and accessibility checks (designer), fixed seeds and a logged baseline (data-scientist), tie-outs to a source file and row (accountant).
- **Never** let the AI change a check to make it pass.

### 3. Session-Based Workflow
Development happens in bounded units called "Sessions".

- **Start**: Load Context → Define Goal.
- **Execute**: Work on *one* thing.
- **End**: Document what changed → Update Context.
- **Why?**: Prevents "context drift" where the AI forgets the plan.
- **Where**: every session belongs to one role and stays inside `workspaces/<role>/`. The plan lives in `workspaces/<role>/plans/sessions/`, the handoff in `workspaces/<role>/plans/transitions/latest.md`.

### 4. Context-First Architecture
The AI is only as smart as its context.

- **Explicit Context**: We don't rely on the AI guessing the stack. We define it in `.cursor/context.md`, one `## Persona: <role>` block per active persona (Workspace, Stack, Architecture Shape, Active Phase).
- **Rule Enforcement**: Rules are installed per role in `.cursor/rules/<role>/` and scoped to `workspaces/<role>/**`, so several personas share one repo without their rules colliding.
- **Strictness**: We acknowledge that legacy code requires different rules than new code.

### 5. The "Vibe"
- **Explicit is better than implicit.**
- **Consistency is better than cleverness.**
- **Files are cheap; confusion is expensive.** (Split code into modules).

---

## Personas

The Adaptive SDLC runs underneath all five roles. What changes per persona is the *vocabulary*, *deliverable*, and *tooling*, not the phase-based discipline.

Several personas can be active in one repo. `/set-persona add <role>` adds one, `/set-persona list` shows them, `/set-persona remove <role>` removes one. Each persona's contract (workspace, stacks, in-session commands, quality gate) is `personas/<role>/persona.yaml`, and every command reads it.

### Shared foundation

All personas follow the same pipeline:
1. `/set-persona add <role>` → `/setup-stack <role>` (every persona has a stack)
2. `/architect <role> @exercises/<role>/<exercise>/README.md`, then the review gate: read the plan, reply "approved"
3. `/start-session <role>`: load context, state goal
4. Work using the persona's in-session commands (see table below)
5. `/next-session`: run the quality gate, document state, log handoffs

| Persona | In-session commands (run during a `/start-session`) |
|---|---|
| **engineer** | `/engineer-tasks` → `/engineer-implement` (TDD red/green/refactor); plus `/code-review`, `/research` |
| **designer** | `/designer-extract` → `/designer-compose` → `/designer-iterate` → `/designer-handoff` |
| **pm** | `/pm-decompose` → `/pm-validate` → `/pm-report` |
| **data-scientist** | `/ds-explore` → `/ds-experiment` → `/ds-validate` → `/ds-handoff` |
| **accountant** | `/acct-reconcile` → `/acct-variance` → `/acct-je-test` → `/acct-close-handoff` |

These commands are spokes of the session loop: they only make sense inside an active session. Don't call them standalone.

Engineers build the Blog API (`exercises/engineer/`, phases 00 to 05) in any of six stacks and are graded by `exercises/engineer/run-acceptance.sh <phase>`. The other roles work on Northwind Co. data in `exercises/_data/northwind/`.

All personas use the same quality loop:
- Universal commands (`/architect`, `/code-review`, etc.) adapt their output per role
- Subagents handle isolated tasks without polluting the main context
- Hooks enforce quality guardrails automatically

### What's different per persona

| | Engineer | Designer | PM | Data Scientist | Accountant |
|---|---|---|---|---|---|
| **Deliverable** | Tested code | Components built from tokens | PRD + tickets | Experiment + model card | Reconciliations, flux, JE tests |
| **Quality gate** | Acceptance + unit tests pass, security clean | Tokens used + logic intact | INVEST + AC format | Seed set + reproducible | Every number ties to a source row |
| **Primary MCPs** | Playwright, context7 | Playwright, context7 | none | Northwind data, context7 | Northwind data |
| **Handoff artifact** | PR | Handoff spec | Jira-ready tickets | model card | close memo |

MCP servers come from `personas/<role>/mcp.json`.

### Cross-persona handoff

The capstone (`exercises/capstone/README.md`) passes one Northwind feature, a receipt fast-track for expense claims, through four personas:
1. PM writes the PRD with the eligibility rule and acceptance criteria
2. Designer adds the fast-track states to the components, consuming the PRD
3. Data Scientist counts the claims that would qualify, with a fixed seed
4. Accountant shows the effect on the accrual and names the compensating control

Engineers stay on the Blog API track; one who finishes phase 05 early adds a second persona and takes a capstone step. Each persona writes only to its own workspace and reads the others. The shared workflow vocabulary (specs, plans, sessions, acceptance criteria) is what makes this handoff clean.

---

## Command Reference

These commands live in `.cursor/commands/` and run in Cursor chat with the `/` prefix. Commands that act on one persona take `<role>`; with a single active persona you can leave it out.

### Setup Commands

#### `set-persona` (`/set-persona add|list|remove <role>`)
**Purpose**: Install, list or remove persona packs. Runs first. Several personas can be active at once.

**What it does:**
1. Copies the persona's commands and agents into `.cursor/`, its rules into `.cursor/rules/<role>/` and its hook scripts into `.cursor/scripts/<role>/`.
2. Merges its hooks into `.cursor/hooks.json` (scoped to `workspaces/<role>/`) and its MCP servers into `.cursor/mcp.json`.
3. Adds a `## Persona: <role>` block to `.cursor/context.md` and creates `workspaces/<role>/`.
4. Writes `.cursor/personas/<role>.manifest.json` (used by `remove` and `/undo persona <role>`).

#### `setup-stack` (`/setup-stack <role>`)
**Purpose**: Configure one persona's technology stack from the built-in library. Runs AFTER `/set-persona`. Every persona has stacks, pm and designer included.

**What it does:**
1. Reads `## Active Personas` from `.cursor/context.md`. Fails if `<role>` is not active.
2. Shows the stack menu from `personas/<role>/persona.yaml` → `stacks` (the first one is the default).
3. If you need a stack that's not in the list, offers `new` to scaffold a custom one from `stacks/blank/`.
4. **Reconciles with existing work**: scans `workspaces/<role>/` and prompts before overwriting (overwrite / skip / merge).
5. Writes `Stack`, `Architecture Shape` and `Active Phase` into the `## Persona: <role>` block of `.cursor/context.md`.
6. Copies `stacks/{selection}/rules/*` to `.cursor/rules/<role>/stack-*.mdc`, and templates, examples and vibe guides to `workspaces/<role>/`.
7. Writes `.cursor/stacks/<role>.manifest.json` listing every file installed (used by `/undo stack <role>`).
8. Recommends `/architect <role>` as the next command.

**For brownfield projects**, use `/detect-stack <role>` instead: it scans your existing repo and generates a stack config from observed patterns.

**When to use:** Right after adding a persona, for every persona.

#### `detect-stack` (`/detect-stack <role> [path]`)
**Purpose**: Automatically analyze an existing codebase to generate custom configuration.

**What it does:**
1. Scans for stack indicators (`package.json`, `requirements.txt`, `go.mod`, etc.) in `workspaces/<role>/` or the path you give
2. Analyzes coding style, architecture patterns, and testing frameworks
3. Installs the detected rules into `.cursor/rules/<role>/` and fills the `## Persona: <role>` block
4. Sets `Strictness: Low` by default for brownfield projects
5. Optionally creates a reusable stack in `stacks/{name}/`

**When to use:** When adding AI assistance to legacy or existing codebases (Workflow 3).

---

### Development Commands

#### `architect` (`/architect <role> [@plan | "description"]`)
**Purpose**: Execute Phase 0 - Design the surface and create a walking skeleton.

**What it does:**
1. Reads the persona's Stack and Architecture Shape from its `## Persona: <role>` block (stops if the stack is unset)
2. Designs the contract for that shape (OpenAPI for REST, a proto for gRPC, PRD sections for pm, tokens and components for designer, notebook or pipeline steps for data-scientist, workpapers for accountant), plus the data model (entities, relationships) where the shape has one
3. Writes the plan to `workspaces/<role>/plans/` (interface contract, session files) and runs a self-audit
4. **Stops at the review gate.** Nothing is built until you reply "approved"
5. After approval, creates the skeleton with mock content in `workspaces/<role>/`

**When to use:** At the start of each exercise or project, after the stack is configured. In class, pass the exercise brief with `@` (Plan Extraction Mode). `/architect` also covers domain modeling (entities and API for a new business domain), which used to be a separate command.

**Example:** `/architect engineer @exercises/engineer/00-skeleton/README.md` or `/architect engineer "Build a user authentication system"`

#### `start-session` (`/start-session <role>`)
**Purpose**: Load context and begin a development session.

**What it does:**
1. Reads the `## Persona: <role>` block in `.cursor/context.md` and `personas/<role>/persona.yaml`
2. Loads the role's rules from `.cursor/rules/<role>/`, the current session file and the last handoff
3. Displays current stack, phase, and strictness level
4. Asks for session goal
5. Enforces rules during the work, inside `workspaces/<role>/`

**When to use:** At the beginning of every session, after running `/architect <role>` and approving its plan.

---

### Quality & Research Commands

#### `research` (`/research "<question>"`)
**Purpose**: Deep investigation using rigorous 3-cycle validation.

**What it does:**
1. **Cycle 1 - Broad Exploration:** Form hypothesis → 5 web searches → refute → refine
2. **Cycle 2 - Deep Dive:** Refined hypothesis → 5 targeted searches → validate → polish
3. **Cycle 3 - Edge Cases:** Final hypothesis → integration checks → sanity check → conclude
4. Outputs research artifact with executive summary, findings, trade-offs, proposed plan

**When to use:** When stuck, investigating new technologies, or solving complex architectural problems.

**Critical:** Does NOT modify code - only researches and documents findings.

**Example:** `/research "Best way to handle distributed locking in Redis"` or `/research "How should we size a flux threshold for accrued reimbursements?"`

#### `research-export` (`/research-export "<topic>"`)
**Purpose**: Generate a structured document to share with external experts or team members.

**What it does:**
1. Gathers current context and problem description
2. Creates `research-exports/research-{topic}-{date}.md` with:
   - Problem statement
   - Attempted solutions
   - Relevant code snippets
   - Specific questions

**When to use:** When you need to escalate a problem or get external review.

#### `code-review` (`/code-review [<role>]`)
**Purpose**: Comprehensive audit of one persona's workspace against its persona and stack rules.

**What it does:**
1. Loads the persona block, `.cursor/rules/<role>/` and strictness level; scope is `workspaces/<role>/` only
2. Security audit (secrets, injection vulnerabilities, dependency versions)
3. Style check (naming conventions, type safety, complexity)
4. Testing gaps (coverage, assertion quality), plus the persona's `review_focus` from `persona.yaml` (for example token discipline for designer, tie-outs for accountant)
5. Outputs violation report and suggestions

**When to use:** Before committing, before phase transitions, or periodic quality checks.

#### `next-session` (`/next-session [<role>]`)
**Purpose**: Wrap up current work and generate transition summary.

**What it does:**
1. Analyzes what files were changed in `workspaces/<role>/`
2. Runs the persona's quality gate (tests for engineers, the matching check for other roles)
3. Ticks the session file's acceptance criteria and advances Active Phase in the persona block only if all are met
4. Writes `workspaces/<role>/plans/transitions/latest.md` with:
   - Session status (success/fail)
   - Where you stopped
   - Next immediate step
   - Context files to load

**When to use:** At the end of a coding session, before switching tasks.

#### `read` (`/read [<role>]`)
**Purpose**: Quick context load to understand current project state.

**What it does:**
1. Reads `.cursor/context.md`: every active persona, or just `<role>`
2. Reads that persona's rules and `persona.yaml`
3. Checks for active session tracking files and the last transition doc
4. Outputs summary per persona: Stack, Current Phase, Next Step

**When to use:** When rejoining a project or starting a new session quickly.

---

### Infrastructure Commands

#### `dockerize` (`/dockerize engineer`)
**Purpose**: Containerize the application with Docker and Docker Compose.

**What it does:**
1. Reads the stack from the persona block; builds from `workspaces/<role>/`
2. Analyzes application (entry point, dependencies, database)
3. Generates multi-stage `Dockerfile` optimized for the stack
4. Generates `docker-compose.yml` with app + database + health checks
5. Generates `.dockerignore` with appropriate exclusions
6. Creates or updates `.env.example` with environment variables
7. Adds `/health` endpoint if missing

**When to use:** After Phase 0 skeleton is complete, or when preparing for deployment (engineer phase 05 asks for Docker).

**Example:**
```
/dockerize engineer
```

**Key features generated:**
- Multi-stage builds (smaller images)
- Non-root user (security)
- Health checks (reliability)
- Environment variables via .env (no secrets in image)

#### `undo` (`/undo persona <role>` | `stack <role>` | `all`)
**Purpose**: Reverse an install using the manifests that `/set-persona` and `/setup-stack` wrote. It never deletes your work in `workspaces/<role>/`.

---

## Workflow Chains

Here's how to chain commands together for each of the three core workflows.

### Chain 1: Fresh Project with Known Stack

**Goal:** Start a new project using a pre-built stack. This is the chain every persona follows in class.

**Sequence:**
```
1. set-persona add   → Add your role
2. setup-stack       → Select stack (e.g., go-gin for engineer, pm-prd-markdown for pm)
3. architect         → Design the surface, review gate, skeleton
4. start-session     → Begin implementation
5. (work)            → Implement one item at a time, check first
6. code-review       → Audit quality
7. next-session      → Wrap up and plan next work
```

**Example flow (engineer, Blog API, any stack):**
```
/set-persona add engineer
/setup-stack engineer
→ Select "go-gin" (or any of the six)
→ Rules copied to .cursor/rules/engineer/, persona block filled

/architect engineer @exercises/engineer/00-skeleton/README.md
→ Contract taken from exercises/engineer/contract/openapi.yaml
→ Plan in workspaces/engineer/plans/, review gate: "approved"
→ Skeleton with mocked endpoints created

/start-session engineer
→ Context loaded: go-gin, Phase 0
→ Implement the skeleton, then exercises/engineer/run-acceptance.sh 00

/code-review
→ Security: ✓ No secrets
→ Style: ✓ Stack rules followed
→ Tests: ⚠️ Missing test for error case

/next-session
→ Status: Phase 0 complete
→ Next: Start Phase 1 (01-auth)
```

**Other roles** run the same chain against their own exercise folder: `/architect pm @exercises/pm/01-notes-to-prd/README.md`, `/architect accountant @exercises/accountant/01-october-bank-rec/README.md`, and so on. Their "tests" are the role checks from principle 2.

### Chain 2: Fresh Project with Custom Stack

**Goal:** Start a new project with a technology stack not in the template library.

**Sequence:**
```
1. (Manual) Create stacks/{name}/ structure
2. (Manual) Write context.md and rules/*.mdc
3. (Manual) Add {name} to personas/<role>/persona.yaml → stacks
4. setup-stack       → Select your new stack (or type "new" at the menu)
5. architect         → Design API surface
6. start-session     → Begin implementation
7. (code)            → Implement features
```

**Example flow:**
```
# Manual steps
mkdir -p stacks/ruby-rails/rules
# Create stacks/ruby-rails/context.md
# Create stacks/ruby-rails/rules/*.mdc
# Add ruby-rails to personas/engineer/persona.yaml → stacks

/setup-stack engineer
→ Select "ruby-rails"
→ Custom rules loaded into .cursor/rules/engineer/

/architect engineer "Build a Rails API for e-commerce"
→ Design follows Rails conventions
→ Skeleton with ActiveRecord models

/start-session engineer
→ Context loaded: Ruby on Rails, Phase 0
→ Begin implementation
```

A Rails Blog API is still graded by `exercises/engineer/run-acceptance.sh`, because the graders only speak HTTP.

### Chain 3: Existing Codebase (Brownfield)

**Goal:** Add AI assistance to a legacy project.

**Sequence:**
```
1. (Manual) Copy .cursor/, personas/ and stacks/ into existing repo
2. set-persona add   → Add your role (code goes under workspaces/<role>/)
3. detect-stack      → AI analyzes codebase
4. (Manual) Review context, set Strictness: Low
5. start-session     → Begin working on new features only
6. (code)            → Add new features with full standards
7. code-review       → Audit new code only
```

**Example flow:**
```
# Manual: cp -r cursor-course-templates/.cursor cursor-course-templates/personas cursor-course-templates/stacks .

/set-persona add engineer
/detect-stack engineer
→ Detected: Python 3.9, Flask, SQLAlchemy
→ Architecture: Flat structure
→ Testing: Pytest present
→ Generated rules with Strictness: Low

# Manual: Review the "## Persona: engineer" block in .cursor/context.md
# and .cursor/rules/engineer/stack-*.mdc, confirm Strictness: Low

/start-session engineer
→ Context loaded: Python Flask (Legacy), Strictness: Low
→ Rules apply to NEW code only

# Implement new /api/v2/users endpoint with full standards
# Existing /api/v1/ endpoints remain unchanged

/code-review
→ New code: ✓ Full type hints, ✓ Tests, ✓ Standards
→ Legacy code: (ignored per Strictness: Low)
```

---

## Creating Custom Stacks

### When to Create a Stack in `stacks/{name}/`

You should create a custom stack in two scenarios:

1. **Workflow 2**: You need a technology stack not in the built-in library (Ruby, Elixir, Scala, etc.)
2. **Workflow 3**: After running `detect-stack`, you want to save the detected configuration as a reusable stack

### Required Directory Structure

```
stacks/{name}/
├── context.md          # REQUIRED: Tech stack definition
├── rules/              # REQUIRED: Coding standards and workflow rules
│   ├── style.mdc       # Naming conventions, formatting
│   ├── testing.mdc     # TDD rules, test patterns
│   └── ...             # Additional rules as needed
├── templates/          # OPTIONAL: Scaffolding files
├── examples/           # OPTIONAL: Reference implementations
└── vibe/               # OPTIONAL: Documentation and guides
```

### Required: context.md

Minimum structure (see `stacks/blank/context.md`):

```markdown
# Project Context: {Stack Name}

## Architecture Shape
{One line, e.g. "REST API (Controller → Service → Repository)". /setup-stack and /architect read it}

## Tech Stack
- Language: {Language + Version}
- Framework: {Framework}
- Database: {Database}
- Testing: {Test Framework}
- Linting: {Linter}

## Vibe & Style
- Coding Style: {Naming conventions}
- Architecture: {Pattern - MVC/Layered/Hexagonal/etc.}

## Key Rules
- {Core rule 1}
- {Core rule 2}
- {Core rule 3}

## Active Phase
- Current: Phase 0 (Skeleton)
```

### Required: rules/ Directory

Create `.mdc` files for different aspects of your stack. Common patterns:

- `000-core-workflow.mdc`: Phase-based development rules
- `100-style.mdc`: Naming, formatting, code organization
- `200-testing.mdc`: TDD rules, test structure
- `300-architecture.mdc`: Layering, dependency rules
- `400-security.mdc`: Security best practices

See `stacks/python-fastapi/rules/` for comprehensive examples.

### Optional: templates/ Directory

Scaffolding files that will be copied to `workspaces/<role>/templates/` when the stack is selected:

```
templates/
├── .env.example           # Environment variables template
├── docker-compose.yml     # Development infrastructure
├── Makefile              # Common commands
└── src/
    └── main.{ext}        # Entry point boilerplate
```

### Optional: examples/ Directory

Reference implementations showing how to use the stack:

```
examples/
├── auth-example/         # Complete authentication example
├── crud-example/         # CRUD operations example
└── testing-example/      # Testing patterns example
```

### Optional: vibe/ Directory

Documentation and guides specific to your stack (copied to `workspaces/<role>/docs/vibe/`):

```
vibe/
├── phase_workflow.md         # Phase-based development guide
├── architecture.md           # Architecture decisions
├── database.md              # Database patterns
└── deployment.md            # Deployment guide
```

### Example: Minimal Custom Stack

For a minimal custom stack, you only need:

```bash
# Create structure
mkdir -p stacks/my-stack/rules

# Create context.md
cat > stacks/my-stack/context.md <<EOF
# Project Context: My Stack

## Architecture Shape
REST API (Controllers → Services → Repositories)

## Tech Stack
- Language: TypeScript 5.0
- Framework: Express.js
- Database: PostgreSQL
- Testing: Jest

## Vibe & Style
- Coding Style: camelCase
- Architecture: Layered (Controllers/Services/Repositories)

## Key Rules
- Use async/await, never callbacks
- All functions must have TypeScript types
- TDD: Write tests before implementation

## Active Phase
- Current: Phase 0 (Skeleton)
EOF

# Create basic rule
cat > stacks/my-stack/rules/style.mdc <<EOF
---
description: TypeScript coding standards
alwaysApply: true
---

# Style Guide

- Use camelCase for variables and functions
- Use PascalCase for classes and interfaces
- Use async/await instead of promises or callbacks
- Add explicit return types to all functions
EOF

# Add my-stack to personas/engineer/persona.yaml → stacks,
# then run /setup-stack engineer and select "my-stack"
```

---

## Best Practices

1. **Start Simple**: Begin with Workflow 1 (known stack) to learn the methodology
2. **One Thing at a Time**: Use `/start-session <role>` to focus on a single goal per session
3. **Trust the Process**: Follow Phase 0 → Phase 1 → Phase 2 even when it feels slow
4. **Research Before Coding**: Use `/research` when uncertain - it's faster than trial and error
5. **Review Regularly**: Run `/code-review` before committing or phase transitions
6. **Document Transitions**: Use `/next-session` to maintain context across work sessions
7. **Strictness Levels Matter**: Set `Strictness: Low` for brownfield, `High` for greenfield
8. **Reuse Stacks**: Once you create a custom stack, commit it to `stacks/` for future projects
9. **Stay in Your Workspace**: Write only to `workspaces/<role>/`. Read other roles' workspaces, hand off through files, and switch roles with `/next-session` then `/start-session <other-role>`
10. **Never Edit the Check**: If an acceptance test, INVEST check or tie-out fails, fix the work, not the check

---

## The Philosophy

This template embodies a fundamental truth: **AI is context-hungry**.

Generic prompts produce generic code. But when you give the AI:
- A clear persona and technology stack (`.cursor/context.md`, one block per persona)
- Explicit rules (`.cursor/rules/<role>/*.mdc`)
- A structured workflow (Phase-Based Development)
- Bounded sessions (start-session → code → next-session)

...you get consistent, professional, maintainable code that follows your standards.

The methodology works because it treats AI like a junior developer who needs clear guidance, not a magic solution that reads your mind.

**Explicit is better than implicit. Consistency is better than cleverness.**
