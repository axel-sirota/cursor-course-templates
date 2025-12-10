# Quickstart Guide 🚀

Welcome to the **AI-Assisted Development Template**. This guide will help you start a new project or adapt an existing one in minutes.

**Works with both Cursor IDE and Claude Code.**

---

## 1. Prerequisites

Before you begin, ensure you have:
-   **Choose your tool**:
    -   **Cursor IDE**: [Download here](https://cursor.sh) *OR*
    -   **Claude Code**: [Installation guide](https://docs.claude.com/en/docs/claude-code/overview)
-   **Docker Desktop**: Running (required for databases)
-   **Git**: Installed

---

## 2. Choose Your Path

### Path A: Start a New Project (The Clean Slate)
*Best for: New ideas, hackathons, learning.*

1.  **Clone the Template**:
    ```bash
    git clone https://github.com/your-org/cursor-course-templates my-new-project
    cd my-new-project
    rm -rf .git  # Detach from template history
    git init     # Start fresh
    ```

2.  **Choose your tool**:

    **Option A: Cursor IDE**
    ```bash
    cursor .
    ```
    Then open the Chat (`Cmd+L`) and type: **`@setup-stack`**

    **Option B: Claude Code**
    ```bash
    claude
    ```
    Then type: **/setup-stack**

3.  **Run Setup**: Follow the prompts from the command above.

4.  **Select Your Stack**:
    -   `python-fastapi` (Reference implementation)
    -   `node-express` (TypeScript)
    -   `java-spring` (Enterprise)
    -   `go-gin` (Performance)
    -   `blank` (Custom)

5.  **Start Building**:
    -   Cursor: **`@architect "Build a [Idea]"`**
    -   Claude Code: **/architect "Build a [Idea]"**

---

### Path B: Adapt an Existing Project (The Rescue Mission)
*Best for: Legacy codebases, refactoring, adding AI powers.*

1.  **Copy the Configuration**:

    **For Cursor**:
    ```bash
    cp -r /path/to/cursor-course-templates/.cursor .
    cursor .
    ```

    **For Claude Code**:
    ```bash
    cp -r /path/to/cursor-course-templates/.claude .
    cp /path/to/cursor-course-templates/CLAUDE.md .
    claude
    ```

2.  **Run Detection**:
    -   Cursor: **`@detect-stack`**
    -   Claude Code: **/detect-stack**

3.  **Review Context**:
    The Agent will generate a context file based on your codebase.
    -   **Check**: Does it match your reality?
    -   **Strictness**: Ensure it is set to `Low` initially to avoid "Linter Hell".

---

### Path C: Enterprise / Monorepo (The Hybrid)
*Best for: Teams with multiple services (e.g., Python Backend + Node Frontend).*

1.  **Setup**:
    Follow Path A (Clone).

2.  **Configure Context**:
    Manually edit `.cursor/context.md` to define your multiple services.
    ```markdown
    ## Tech Stack
    - **Backend**: Python FastAPI (services/api)
    - **Frontend**: React (services/web)
    ```

3.  **Scope Rules**:
    Go to `.cursor/rules/` and duplicate rules if needed, adding `glob` patterns:
    -   `python-standards.mdc`: `globs: "services/api/**/*.py"`
    -   `react-standards.mdc`: `globs: "services/web/**/*.tsx"`

---

## 3. Common Workflows

### "I want to build a feature"
1.  **Design**: `@architect` (Cursor) or `/architect` (Claude Code)
2.  **Plan**: Review `plan/sessions/`
3.  **Execute**: `@start-session` or `/start-session`

### "I am stuck / It's broken"
1.  **Research**: `@research` or `/research`
2.  **Export**: `@research-export` or `/research-export` (share with team)

### "I want to verify my code"
1.  **Review**: `@code-review` or `/code-review`
2.  **Tests**: Run the command specific to your stack (`pytest`, `npm test`, etc.)

---

## 4. Troubleshooting

| Issue | Fix |
| :--- | :--- |
| **Agent suggests wrong stack** | Run setup command again and check context file (`.cursor/context.md` or `CLAUDE.md`). |
| **"Command not found"** | Ensure commands folder exists (`.cursor/commands/` or `.claude/commands/`). |
| **Docker fails** | Run `docker-compose down -v` to reset state. |
| **Too many linter errors** | Edit context file -> Set `Strictness: Low`. |

---

## 5. Next Steps
-   Read **[METHODOLOGY.md](METHODOLOGY.md)** to understand the "Phase-Based Workflow".
-   Check **[ADAPTATION_GUIDE.md](ADAPTATION_GUIDE.md)** to add custom stacks.

