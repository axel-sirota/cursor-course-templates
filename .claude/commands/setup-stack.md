---
description: Configure the project stack, rules, and context (Start Here)
---

# Setup Stack Command

This command guides the user through configuring the project's technology stack and development rules. It is the entry point for "activating" the Master Template.

## Stack Shape Reference

This command is stack- and shape-agnostic. It must work identically for a Web API, a CLI, Terraform/IaC, a library, a UI-only project, or anything else — including a project with no standard stack at all (the `blank` stack). Never assume the target is a web service, and never assume a manifest file like `package.json` is the only valid signal of a project's shape. The **shape** (Web API / CLI / Terraform / Library / UI-only / Other) is recorded in the generated `CLAUDE.md` as the **Architecture Shape** field and is consumed downstream by `/architect`.

## Execution Flow

**1. Greeting & Selection**
Ask the user which setup path they want to take:

> "Welcome to the Context-Aware Master Template. How would you like to configure this project?
> 
> 1.  **Standard Stack**: Select from a built-in library (Python, Node, Go, Terraform, or a blank/custom stack).
> 2.  **From Plan**: Analyze a project plan/requirements document to generate a stack.
> 3.  **Analyze Code**: Scan the current files to detect an existing stack (Brownfield)."

**2. Path Handlers**

### Path 1: Standard Stack
1.  List available stacks by reading the actual contents of the `stacks/` directory (e.g. `ls stacks/`) — do not hardcode a fixed list, since new stacks can be added over time. As of this writing that directory includes entries such as:
    - `python-fastapi`
    - `java-spring`
    - `node-express`
    - `go-gin`
    - `devops-terraform`
    - `blank` (no preset language/framework — for a custom or not-yet-standard stack)
    Always present whatever `stacks/` actually contains, including `blank`, so a project with no standard-stack match still has an explicit, listed option.
2.  Ask user to confirm selection.
3.  **Action**:
    - If `stacks/{selection}/rules/` exists, copy `stacks/{selection}/rules/*` to `.claude/rules/`.
    - If `stacks/{selection}/rules/` does NOT exist (e.g. the `blank` stack), skip the copy and tell the user: "No preset rules for this stack — rules are aspirational until you add your own to `.claude/rules/`."
    - Copy `stacks/{selection}/context.md` to `CLAUDE.md` (overwrite).
    - **Asset Copy**:
      - If `stacks/{selection}/vibe/` exists, copy it to `vibe/` in root (Documentation).
      - If `stacks/{selection}/templates/` exists, copy it to `templates/` in root (Scaffolding assets).
    - If `stacks/{selection}/examples/` exists, ask if they want to see them.
    - **Initialize Shared Phase State (MANDATORY)**: Create `plan/PHASES.md` if it does not already exist, using this exact minimal schema (this is the same file format read/written by `/architect`, `/start-session`, and `/next-session` — do not invent a different filename or shape):
      ```markdown
      # Project Phases

      current_phase: 0
      current_status: not_started   # not_started | in_progress | blocked | complete

      ## Phase 0: Skeleton
      - Status: not_started
      - Goal: Define via /architect
      - Done:
        - (none yet)
      - Pending:
        - Run /architect to design the skeleton and break down phases
      ```
      If `plan/PHASES.md` already exists (e.g. re-running `/setup-stack` on an already-architected project), leave it untouched — do not overwrite existing phase history.
4.  **Verification**: Read `CLAUDE.md` and confirm the stack is active. Confirm `plan/PHASES.md` exists.

### Path 2: From Plan (The "Architect" Path)
1.  Ask the user to paste their plan or provide a file path.
2.  **Analysis**: Read the plan and extract:
    - Language & Framework (if any — a plan may describe infra, a CLI, or a library with no "framework" in the web sense)
    - Architecture Shape: is this a Web API, a CLI, Terraform/IaC, a Library, a UI-only project, or Other? Record this explicitly.
    - Database & Infrastructure (if applicable)
    - Key Architectural Patterns
    - Testing Strategy
3.  **Generation**:
    - Create a custom content for `CLAUDE.md` based on the plan, including the detected **Architecture Shape**.
    - Ask the user to confirm the extracted details.
4.  **Rule Selection**:
    - Identify the *closest matching* Standard Stack based on the plan's actual shape — do not default to a web-framework stack just because one happens to be listed first:
      - If the plan describes a web service/API (e.g. "Django", "Express", "Spring"), match the closest language's web stack (e.g. `python-fastapi`, `node-express`, `java-spring`, `go-gin`) as a base.
      - If the plan describes infrastructure/IaC (Terraform, Pulumi, CloudFormation, etc.), match `devops-terraform`.
      - If the plan describes a CLI, a library, or anything with no HTTP/service surface, match the closest language-only base, or match `blank` if no close base exists — do not force it into a web-framework stack.
    - Copy those rules to `.claude/rules/` (if the matched stack has a `rules/` directory; if it does not — e.g. `blank` — skip and tell the user rules are aspirational until they add their own).
    - **Note**: Explicitly mention if some rules might need manual adjustment.
    - **Initialize Shared Phase State (MANDATORY)**: Same as Path 1 step 3 — create `plan/PHASES.md` with the exact schema shown there if it does not already exist. Leave existing files untouched.

### Path 3: Analyze Code (The "Brownfield" Path)
1.  **Scan**: List files in the root directory. Look broadly across shapes, not just application manifests:
    - Application/library manifests: `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `pom.xml`, etc.
    - Infrastructure-as-code signals: `*.tf`, `main.tf`, `backend.tf`, `Pulumi.yaml`, CloudFormation templates, etc.
    - If none of the above are found, do not guess — treat this as a candidate for the `blank` stack and tell the user no standard stack was auto-detected.
2.  **Detection**: Identify the primary language and framework, and the **Architecture Shape** (Web API / CLI / Terraform-IaC / Library / UI-only / Other / Undetected).
3.  **Quality Check**:
    - Are there tests? (`tests/` folder, or shape-appropriate equivalent such as `*_test.go`, `*.tftest.hcl`) -> Set Strictness: High/Medium.
    - Are there type definitions / schemas? -> Set Strictness: High/Medium.
4.  **Generation**:
    - Create a `CLAUDE.md` reflecting the detected state, including the detected (or "Undetected — treated as blank") **Architecture Shape**.
    - Set `Strictness` level (Low/Medium/High) to adjust rule enforcement.
5.  **Rule Selection**:
    - Copy relevant base rules for the detected/matched stack (if that stack has a `rules/` directory).
    - If no stack was detected, fall back to the `blank` stack: no rules to copy, and tell the user rules are aspirational until they add their own to `.claude/rules/`.
    - *Crucial*: If "Strictness" is Low, instruct the user that rules are "aspirational" for legacy code but mandatory for new code.
    - **Initialize Shared Phase State (MANDATORY)**: Same schema as Path 1 step 3. Since code already exists in a brownfield project, set `current_status: in_progress` and Phase 0's `Status: in_progress` instead of `not_started`, and list what already exists under `Done` (e.g. "Existing codebase scaffolded") with a `Pending` item to "Run /architect to confirm/complete the skeleton and break down remaining phases." If `plan/PHASES.md` already exists, leave it untouched.

**3. Finalize**
- Remind the user: "You can always update `CLAUDE.md` manually to tweak settings."
- Confirm `plan/PHASES.md` was created (or already existed) before finishing.
- Suggest the next step based on state: if Phase 0 is `not_started`, suggest running `/architect` to design the skeleton and establish the phase breakdown; if a phase is already `in_progress` (e.g. brownfield with existing work), suggest running `/start-session` to resume.

