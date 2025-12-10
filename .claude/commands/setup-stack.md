---
description: Configure the project stack, rules, and context (Start Here)
---

# Setup Stack Command

This command guides the user through configuring the project's technology stack and development rules. It is the entry point for "activating" the Master Template.

## Execution Flow

**1. Greeting & Selection**
Ask the user which setup path they want to take:

> "Welcome to the Context-Aware Master Template. How would you like to configure this project?
> 
> 1.  **Standard Stack**: Select from a built-in library (Python, Node, Go, etc.).
> 2.  **From Plan**: Analyze a project plan/requirements document to generate a stack.
> 3.  **Analyze Code**: Scan the current files to detect an existing stack (Brownfield)."

**2. Path Handlers**

### Path 1: Standard Stack
1.  List available stacks in `stacks/` directory:
    - `python-fastapi`
    - `java-spring`
    - `node-express`
    - `go-gin`
    - `devops-terraform`
2.  Ask user to confirm selection.
3.  **Action**:
    - Copy `stacks/{selection}/rules/*` to `.claude/rules/`.
    - Copy `stacks/{selection}/context.md` to `CLAUDE.md` (overwrite).
    - **Asset Copy**:
      - If `stacks/{selection}/vibe/` exists, copy it to `vibe/` in root (Documentation).
      - If `stacks/{selection}/templates/` exists, copy it to `templates/` in root (Scaffolding assets).
    - If `stacks/{selection}/examples/` exists, ask if they want to see them.
4.  **Verification**: Read `CLAUDE.md` and confirm the stack is active.

### Path 2: From Plan (The "Architect" Path)
1.  Ask the user to paste their plan or provide a file path.
2.  **Analysis**: Read the plan and extract:
    - Language & Framework
    - Database & Infrastructure
    - Key Architectural Patterns
    - Testing Strategy
3.  **Generation**:
    - Create a custom content for `CLAUDE.md` based on the plan.
    - Ask the user to confirm the extracted details.
4.  **Rule Selection**:
    - Identify the *closest matching* Standard Stack (e.g., if plan says "Django", match "Python Generic" or "Python FastAPI" as a base).
    - Copy those rules to `.claude/rules/`.
    - **Note**: Explicitly mention if some rules might need manual adjustment.

### Path 3: Analyze Code (The "Brownfield" Path)
1.  **Scan**: List files in the root directory (look for `package.json`, `requirements.txt`, `go.mod`, `pom.xml`, etc.).
2.  **Detection**: Identify the primary language and framework.
3.  **Quality Check**:
    - Are there tests? (`tests/` folder) -> Set Strictness: High/Medium.
    - Are there type definitions? -> Set Strictness: High/Medium.
4.  **Generation**:
    - Create a `CLAUDE.md` reflecting the detected state.
    - Set `Strictness` level (Low/Medium/High) to adjust rule enforcement.
5.  **Rule Selection**:
    - Copy relevant base rules.
    - *Crucial*: If "Strictness" is Low, instruct the user that rules are "aspirational" for legacy code but mandatory for new code.

**3. Finalize**
- Remind the user: "You can always update `CLAUDE.md` manually to tweak settings."
- Suggest running `/start-session` to begin working.

