# Core Methodology: Agentic SDLC

This document defines the **language-agnostic principles** behind the AI-Assisted Development Template. These principles apply whether you are using Cursor IDE or Claude Code, and whether you are writing Python, Go, TypeScript, Rust, or any other language.

---

## Core Principles

### 1. Phase-Based Development
Software is built in distinct layers, not vertical slices.

- **Phase 0 (Skeleton)**: Build the structure first. Mock every endpoint. Verify the "shape" of the API before writing logic.
- **Phase 1+ (Implementation)**: Implement one endpoint at a time.
- **Why?**: Prevents getting stuck in implementation details before the architecture is proven.

### 2. Test-Driven Development (TDD)
Tests are not "quality assurance"; they are **design tools**.

- **The Rule**: You cannot write implementation code until a test fails.
- **The Flow**: Red (Write Test) → Green (Make it Pass) → Refactor (Clean up).
- **AI Role**: The AI is excellent at writing tests if you give it the skeleton (Phase 0).

### 3. Session-Based Workflow
Development happens in bounded units called "Sessions".

- **Start**: Load Context → Define Goal.
- **Execute**: Work on *one* thing.
- **End**: Document what changed → Update Context.
- **Why?**: Prevents "context drift" where the AI forgets the plan.

### 4. Context-First Architecture
The AI is only as smart as its context.

- **Explicit Context**: We don't rely on the AI guessing the stack. We define it in `.cursor/context.md` (Cursor) or `CLAUDE.md` (Claude Code).
- **Rule Enforcement**: Rules are injected based on the context.
- **Strictness**: We acknowledge that legacy code requires different rules than new code.

### 5. The "Vibe"
- **Explicit is better than implicit.**
- **Consistency is better than cleverness.**
- **Files are cheap; confusion is expensive.** (Split code into modules).

---

## Command Reference

These commands are available in both Cursor IDE (using `@` prefix) and Claude Code (using `/` prefix). The functionality is identical across both tools.

### Setup Commands

#### `setup-stack` (or `@setup-stack` / `/setup-stack`)
**Purpose**: Entry point for configuring your project's technology stack.

**What it does:**
1. Presents three setup paths:
   - **Standard Stack**: Select from built-in library (Python, Node, Go, Java, Terraform)
   - **From Plan**: Analyze a requirements document to generate a stack
   - **Analyze Code**: Scan existing codebase (brownfield)
2. Copies rules from `stacks/{selection}/rules/` to `.cursor/rules/` or `.claude/rules/`
3. Copies `stacks/{selection}/context.md` to `.cursor/context.md` or `CLAUDE.md`
4. Optionally copies templates, examples, and vibe guides

**When to use:** First step when starting any project or adopting the template.

#### `detect-stack` (or `@detect-stack` / `/detect-stack`)
**Purpose**: Automatically analyze an existing codebase to generate custom configuration.

**What it does:**
1. Scans for stack indicators (`package.json`, `requirements.txt`, `go.mod`, etc.)
2. Analyzes coding style, architecture patterns, and testing frameworks
3. Generates custom context file with detected configuration
4. Sets `Strictness: Low` by default for brownfield projects
5. Optionally creates a reusable stack in `stacks/detected-{name}/`

**When to use:** When adding AI assistance to legacy or existing codebases (Workflow 3).

---

### Development Commands

#### `architect` (or `@architect` / `/architect`)
**Purpose**: Execute Phase 0 - Design the API surface and create a walking skeleton.

**What it does:**
1. Reads active stack from context file
2. Designs the API contract (OpenAPI spec for REST, CLI args for CLI tools, Terraform inputs/outputs for IaC)
3. Creates skeleton implementation with mock responses
4. Generates implementation plan broken into sessions

**When to use:** At the start of a new feature or project, after stack is configured.

**Example:** `@architect "Build a user authentication system"` or `/architect "Build a user authentication system"`

#### `start-session` (or `@start-session` / `/start-session`)
**Purpose**: Load context and begin a development session.

**What it does:**
1. Reads context file (`.cursor/context.md` or `CLAUDE.md`)
2. Loads active rules from `.cursor/rules/` or `.claude/rules/`
3. Displays current stack, phase, and strictness level
4. Asks for session goal
5. Enforces rules during coding

**When to use:** At the beginning of every coding session, after running `setup-stack` or `architect`.

#### `start-project` (or `@start-project` / `/start-project`)
**Purpose**: Domain modeling - propose entities and API for a business domain.

**What it does:**
1. Reads context to understand the active language/framework
2. Proposes data model (entities, tables, relationships)
3. Proposes REST API endpoints or CLI commands
4. Generates implementation plan using Phase-Based Workflow

**When to use:** When starting a new business domain or feature that needs data modeling.

**Example:** `@start-project "Library Management System"` or `/start-project "Library Management System"`

---

### Quality & Research Commands

#### `research` (or `@research` / `/research`)
**Purpose**: Deep investigation using rigorous 3-cycle validation.

**What it does:**
1. **Cycle 1 - Broad Exploration:** Form hypothesis → 5 web searches → refute → refine
2. **Cycle 2 - Deep Dive:** Refined hypothesis → 5 targeted searches → validate → polish
3. **Cycle 3 - Edge Cases:** Final hypothesis → integration checks → sanity check → conclude
4. Outputs research artifact with executive summary, findings, trade-offs, proposed plan

**When to use:** When stuck, investigating new technologies, or solving complex architectural problems.

**Critical:** Does NOT modify code - only researches and documents findings.

**Example:** `@research "Best way to handle distributed locking in Redis"` or `/research "Best way to handle distributed locking in Redis"`

#### `research-export` (or `@research-export` / `/research-export`)
**Purpose**: Generate a structured document to share with external experts or team members.

**What it does:**
1. Gathers current context and problem description
2. Creates `research-exports/research-{topic}-{date}.md` with:
   - Problem statement
   - Attempted solutions
   - Relevant code snippets
   - Specific questions

**When to use:** When you need to escalate a problem or get external review.

#### `code-review` (or `@code-review` / `/code-review`)
**Purpose**: Comprehensive audit of codebase against active stack rules.

**What it does:**
1. Loads context and strictness level
2. Security audit (secrets, injection vulnerabilities, dependency versions)
3. Style check (naming conventions, type safety, complexity)
4. Testing gaps (coverage, assertion quality)
5. Outputs violation report and suggestions

**When to use:** Before committing, before phase transitions, or periodic quality checks.

#### `next-session` (or `@next-session` / `/next-session`)
**Purpose**: Wrap up current work and generate transition summary.

**What it does:**
1. Analyzes what files were changed
2. Checks test status
3. Updates Active Phase in context if phase is complete
4. Generates transition document with:
   - Session status (success/fail)
   - Where you stopped
   - Next immediate step
   - Context files to load

**When to use:** At the end of a coding session, before switching tasks.

#### `read` (or `@read` / `/read`)
**Purpose**: Quick context load to understand current project state.

**What it does:**
1. Reads context file (`.cursor/context.md` or `CLAUDE.md`)
2. Reads active rules
3. Checks for active session tracking files
4. Outputs summary: Stack, Current Phase, Next Step

**When to use:** When rejoining a project or starting a new session quickly.

---

## Workflow Chains

Here's how to chain commands together for each of the three core workflows.

### Chain 1: Fresh Project with Known Stack

**Goal:** Start a new project using a pre-built stack.

**Sequence:**
```
1. setup-stack       → Select stack (e.g., python-fastapi)
2. architect         → Design API surface and skeleton
3. start-session     → Begin implementation
4. (code)            → Implement features using TDD
5. code-review       → Audit quality
6. next-session      → Wrap up and plan next work
```

**Example flow:**
```
@setup-stack
→ Select "python-fastapi"
→ Rules copied, context loaded

@architect "Build a blog API with posts and comments"
→ OpenAPI spec created
→ Skeleton with mocked endpoints created
→ Implementation plan generated

@start-session
→ Context loaded: Python FastAPI, Phase 0
→ Begin implementing POST /posts endpoint with TDD

@code-review
→ Security: ✓ No secrets
→ Style: ✓ Type hints present
→ Tests: ⚠️ Missing test for error case

@next-session
→ Status: Phase 0 complete
→ Next: Start Phase 1 (implement POST /posts)
```

### Chain 2: Fresh Project with Custom Stack

**Goal:** Start a new project with a technology stack not in the template library.

**Sequence:**
```
1. (Manual) Create stacks/{name}/ structure
2. (Manual) Write context.md and rules/*.mdc
3. setup-stack       → Select your new stack
4. architect         → Design API surface
5. start-session     → Begin implementation
6. (code)            → Implement features
```

**Example flow:**
```
# Manual steps
mkdir -p stacks/ruby-rails/rules
# Create stacks/ruby-rails/context.md
# Create stacks/ruby-rails/rules/*.mdc

@setup-stack
→ Select "ruby-rails"
→ Custom rules loaded

@architect "Build a Rails API for e-commerce"
→ Design follows Rails conventions
→ Skeleton with ActiveRecord models

@start-session
→ Context loaded: Ruby on Rails, Phase 0
→ Begin implementation
```

### Chain 3: Existing Codebase (Brownfield)

**Goal:** Add AI assistance to a legacy project.

**Sequence:**
```
1. (Manual) Copy .cursor/ or .claude/ into existing repo
2. detect-stack      → AI analyzes codebase
3. (Manual) Review context, set Strictness: Low
4. start-session     → Begin working on new features only
5. (code)            → Add new features with full standards
6. code-review       → Audit new code only
```

**Example flow:**
```
# Manual: cp -r cursor-course-templates/.claude .

@detect-stack
→ Detected: Python 3.9, Flask, SQLAlchemy
→ Architecture: Flat structure
→ Testing: Pytest present
→ Generated context with Strictness: Low

# Manual: Review CLAUDE.md, confirm Strictness: Low

@start-session
→ Context loaded: Python Flask (Legacy), Strictness: Low
→ Rules apply to NEW code only

# Implement new /api/v2/users endpoint with full standards
# Existing /api/v1/ endpoints remain unchanged

@code-review
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

Scaffolding files that will be copied to the project root when the stack is selected:

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

Documentation and guides specific to your stack:

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

# Done! Now run @setup-stack and select "my-stack"
```

---

## Best Practices

1. **Start Simple**: Begin with Workflow 1 (known stack) to learn the methodology
2. **One Thing at a Time**: Use `start-session` to focus on a single goal per session
3. **Trust the Process**: Follow Phase 0 → Phase 1 → Phase 2 even when it feels slow
4. **Research Before Coding**: Use `@research` when uncertain - it's faster than trial and error
5. **Review Regularly**: Run `@code-review` before committing or phase transitions
6. **Document Transitions**: Use `@next-session` to maintain context across work sessions
7. **Strictness Levels Matter**: Set `Strictness: Low` for brownfield, `High` for greenfield
8. **Reuse Stacks**: Once you create a custom stack, commit it to `stacks/` for future projects

---

## The Philosophy

This template embodies a fundamental truth: **AI is context-hungry**.

Generic prompts produce generic code. But when you give the AI:
- A clear technology stack (context.md or CLAUDE.md)
- Explicit rules (rules/*.mdc)
- A structured workflow (Phase-Based Development)
- Bounded sessions (start-session → code → next-session)

...you get consistent, professional, maintainable code that follows your standards.

The methodology works because it treats AI like a junior developer who needs clear guidance, not a magic solution that reads your mind.

**Explicit is better than implicit. Consistency is better than cleverness.**
