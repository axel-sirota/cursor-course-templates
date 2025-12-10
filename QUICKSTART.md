# Quickstart Guide 🚀

Welcome to the **AI-Assisted Development Template**. This guide will help you start a new project or adapt an existing one in minutes.

**Works with both Cursor IDE and Claude Code.**

---

## Prerequisites

Before you begin, ensure you have:

-   **AI Tool** (choose one):
    -   **Cursor IDE**: [Download here](https://cursor.sh) *OR*
    -   **Claude Code**: [Installation guide](https://docs.claude.com/en/docs/claude-code/overview)

**Optional Dependencies:**
-   **Docker**: Only required if your stack uses containerized databases (Python FastAPI, Node Express examples include PostgreSQL in docker-compose)
-   **Git**: Only required if cloning the template from a repository

---

## Three Core Workflows

This template supports three distinct workflows depending on your needs. Choose the one that matches your situation.

---

### Workflow 1: Fresh Project with Known Stack

**Best for:** Starting a new project using a pre-built stack (Python FastAPI, Node Express, Java Spring, Go Gin, DevOps Terraform).

**Steps:**

1.  **Get the Template**
    ```bash
    git clone https://github.com/your-org/cursor-course-templates my-new-project
    cd my-new-project
    ```

2.  **Open in Your AI Tool**

    **Cursor IDE:**
    ```bash
    cursor .
    ```
    Open Chat (`Cmd+L`)

    **Claude Code:**
    ```bash
    claude
    ```

3.  **Configure Stack**

    Run the setup command:
    - **Cursor**: `@setup-stack`
    - **Claude Code**: `/setup-stack`

    Select from available stacks:
    - `python-fastapi` (REST API with PostgreSQL)
    - `node-express` (TypeScript API)
    - `java-spring` (Enterprise Java)
    - `go-gin` (High-performance Go)
    - `devops-terraform` (Infrastructure as Code)
    - `blank` (Minimal template for custom stacks)

4.  **Design Your Feature**

    - **Cursor**: `@architect "Build a task management API"`
    - **Claude Code**: `/architect "Build a task management API"`

    The AI will design the API surface and create a walking skeleton.

5.  **Start Coding**

    - **Cursor**: `@start-session`
    - **Claude Code**: `/start-session`

    The AI loads your stack context and begins implementation.

---

### Workflow 2: Fresh Project with Custom Stack

**Best for:** Building a project with a technology stack not included in the template (e.g., Ruby on Rails, Elixir Phoenix, Kotlin Spring).

**Steps:**

1.  **Get the Template**
    ```bash
    git clone https://github.com/your-org/cursor-course-templates my-new-project
    cd my-new-project
    ```

2.  **Create Your Stack Structure**

    Create a new directory under `stacks/` with this structure:
    ```bash
    mkdir -p stacks/my-stack/rules
    mkdir -p stacks/my-stack/templates  # Optional
    mkdir -p stacks/my-stack/examples   # Optional
    mkdir -p stacks/my-stack/vibe       # Optional
    ```

3.  **Define Stack Context**

    Create `stacks/my-stack/context.md`:
    ```markdown
    # Project Context: My Stack

    ## Tech Stack
    - Language: [Your Language]
    - Framework: [Your Framework]
    - Database: [Your Database]
    - Testing: [Your Test Framework]

    ## Vibe & Style
    - Coding Style: [camelCase/snake_case/PascalCase]
    - Architecture: [MVC/Layered/Hexagonal/etc.]

    ## Key Rules
    - [Your Rule 1]
    - [Your Rule 2]

    ## Active Phase
    - Current: Phase 0 (Skeleton)
    ```

4.  **Create Rules**

    Create `.mdc` files in `stacks/my-stack/rules/`:
    - `style.mdc`: Coding standards
    - `testing.mdc`: Test-driven development rules
    - `architecture.mdc`: Structural patterns

    See `stacks/python-fastapi/rules/` for examples.

5.  **Optional: Add Templates and Examples**

    - `templates/`: Scaffolding files (will be copied to project root)
    - `examples/`: Reference implementations
    - `vibe/`: Documentation and guides

6.  **Configure Your Project**

    Open in your AI tool and run:
    - **Cursor**: `@setup-stack`
    - **Claude Code**: `/setup-stack`

    Select your new stack from the list.

7.  **Start Building**

    - **Cursor**: `@architect "Build X"` → `@start-session`
    - **Claude Code**: `/architect "Build X"` → `/start-session`

---

### Workflow 3: Adapt Existing Codebase

**Best for:** Adding AI-assisted development to a legacy or brownfield project.

**Steps:**

1.  **Copy Configuration to Your Repo**

    **For Cursor IDE:**
    ```bash
    cd /path/to/your-existing-project
    cp -r /path/to/cursor-course-templates/.cursor .
    ```

    **For Claude Code:**
    ```bash
    cd /path/to/your-existing-project
    cp -r /path/to/cursor-course-templates/.claude .
    cp /path/to/cursor-course-templates/CLAUDE.md .
    ```

2.  **Open in Your AI Tool**

    **Cursor IDE:**
    ```bash
    cursor .
    ```

    **Claude Code:**
    ```bash
    claude
    ```

3.  **Detect Your Stack**

    Run the detection command:
    - **Cursor**: `@detect-stack`
    - **Claude Code**: `/detect-stack`

    The AI will:
    - Scan your codebase (`package.json`, `requirements.txt`, `go.mod`, etc.)
    - Analyze coding style, architecture, and testing patterns
    - Generate a custom context file (`.cursor/context.md` or `CLAUDE.md`)
    - Optionally create a reusable stack in `stacks/detected-{name}/`

4.  **Review and Adjust Context**

    Open the generated context file:
    - **Cursor**: `.cursor/context.md`
    - **Claude Code**: `CLAUDE.md`

    **Critical**: Set `Strictness: Low` for legacy codebases
    ```markdown
    ## Strictness: Low
    - Refactoring: Only touch what is necessary
    - New Code: Apply full standards to new features only
    - Legacy Code: Document issues but don't force refactoring
    ```

5.  **Start Working on New Features**

    - **Cursor**: `@start-session`
    - **Claude Code**: `/start-session`

    The AI will respect your existing patterns while writing clean new code.

---

## Command Reference

Once your stack is configured, use these commands during development:

| Command | Cursor | Claude Code | Purpose |
|---------|--------|-------------|---------|
| **Setup Stack** | `@setup-stack` | `/setup-stack` | Configure project with a technology stack |
| **Detect Stack** | `@detect-stack` | `/detect-stack` | Analyze existing code to generate configuration |
| **Architect** | `@architect "Build X"` | `/architect "Build X"` | Design Phase 0 (API surface, skeleton, mocks) |
| **Start Session** | `@start-session` | `/start-session` | Load context and begin coding |
| **Research** | `@research "Question"` | `/research "Question"` | Deep investigation with 3-cycle validation |
| **Code Review** | `@code-review` | `/code-review` | Audit code against stack rules |
| **Next Session** | `@next-session` | `/next-session` | Wrap up and generate transition summary |
| **Read Context** | `@read` | `/read` | Quick context load (stack + phase + next step) |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **"No Stack Configured"** | Run `@setup-stack` (Cursor) or `/setup-stack` (Claude Code) first |
| **AI suggests wrong stack** | Check context file (`.cursor/context.md` or `CLAUDE.md`) and verify stack selection |
| **Command not found** | Ensure `.cursor/commands/` or `.claude/commands/` directory exists |
| **Too many linter errors** | Set `Strictness: Low` in context file for legacy codebases |
| **Docker connection fails** | Only needed if using containerized databases - run `docker-compose down -v` to reset |

---

## Next Steps

-   **Understand the Methodology**: Read [METHODOLOGY.md](METHODOLOGY.md) to learn about Phase-Based Development, TDD, and command workflows
-   **Create Custom Stacks**: Read [ADAPTATION_GUIDE.md](ADAPTATION_GUIDE.md) to build stacks for any language or framework
-   **View Examples**: Check `stacks/python-fastapi/examples/` for reference implementations
