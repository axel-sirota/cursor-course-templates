# Quickstart Guide 🚀

Welcome to the **Cursor Master Template**. This guide will help you start a new project or adapt an existing one in minutes.

---

## 1. Prerequisites

Before you begin, ensure you have:
-   **Cursor IDE**: [Download here](https://cursor.sh)
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

2.  **Open in Cursor**:
    ```bash
    cursor .
    ```

3.  **Run Setup**:
    Open the Chat (`Cmd+L`) and type:
    > **`@setup-stack`**

4.  **Select Your Stack**:
    -   `python-fastapi` (Reference implementation)
    -   `node-express` (TypeScript)
    -   `java-spring` (Enterprise)
    -   `go-gin` (Performance)
    -   `blank` (Custom)

5.  **Start Building**:
    > **`@architect "Build a [Idea]"`**

---

### Path B: Adapt an Existing Project (The Rescue Mission)
*Best for: Legacy codebases, refactoring, adding AI powers.*

1.  **Copy the Brain**:
    Copy the `.cursor/` folder from this repo into your existing project root.
    ```bash
    # From your project root
    cp -r /path/to/cursor-course-templates/.cursor .
    ```

2.  **Open Cursor**:
    ```bash
    cursor .
    ```

3.  **Run Detection**:
    Open Chat and type:
    > **`@detect-stack`**

4.  **Review Context**:
    The Agent will generate a `.cursor/context.md` based on your files.
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
1.  **Design**: `@architect "Add User Profiles"`
2.  **Plan**: Review `plan/sessions/`
3.  **Execute**: `@start-session 1`

### "I am stuck / It's broken"
1.  **Research**: `@research "Why is the DB connection failing?"`
2.  **Export**: `@research-export "Complex Issue"` (share with team)

### "I want to verify my code"
1.  **Review**: `@code-review`
2.  **Tests**: Run the command specific to your stack (`pytest`, `npm test`, etc.)

---

## 4. Troubleshooting

| Issue | Fix |
| :--- | :--- |
| **Agent suggests Python code in Node project** | Run `@setup-stack` again or check `.cursor/context.md`. |
| **"Command not found"** | Ensure `.cursor/commands/` exists. Restart Cursor. |
| **Docker fails** | Run `docker-compose down -v` to reset state. |
| **Too many linter errors** | Edit `.cursor/context.md` -> Set `Strictness: Low`. |

---

## 5. Next Steps
-   Read **[METHODOLOGY.md](METHODOLOGY.md)** to understand the "Phase-Based Workflow".
-   Check **[ADAPTATION_GUIDE.md](ADAPTATION_GUIDE.md)** to add custom stacks.

