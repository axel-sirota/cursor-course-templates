---
description: Automatically detect stack, style, and structure of an existing project
---

# Detect Stack Command

This command analyzes an existing codebase (Brownfield) to generate a custom configuration for ONE persona. It is the "Universal Adapter" for unknown or legacy projects, and the brownfield alternative to `/setup-stack`.

```
/detect-stack                 # if one persona is active, use it; if several, ask which
/detect-stack <role>          # detect the stack for that persona
/detect-stack <role> <path>   # scan <path> instead of workspaces/<role>/
```

## Execution Flow

**0. Pick the persona**
- Read `## Active Personas` from `.cursor/context.md`.
  - Empty or `(none)` → "⚠️ No persona configured. Run `/set-persona add <role>` first, then `/detect-stack <role>`." Stop.
- If `<role>` was given, it must be in the active list. Otherwise: "`<role>` is not active. Run `/set-persona add <role>` first." Stop.
- If no role was given: one active persona → use it. Several → ask "Which persona is this stack for? {list}".
- If `## Persona: <role>` already has a Stack set → "`<role>` already uses `{stack}`. Run `/undo stack <role>` first to switch." Stop.
- **Scan root**: the `<path>` the user gave, otherwise `workspaces/<role>/` (ignore `plans/` and `README.md`). If the scan root has no code, ask the user for the path to their existing code.
- Track every path written in `files` (for the manifest in step 10).

**1. Reconnaissance**
- **Action**: Scan the scan root and its key subdirectories.
- **Look for**:
  - `package.json`, `tsconfig.json` (Node/JS)
  - `requirements.txt`, `pyproject.toml`, `Pipfile` (Python)
  - `pom.xml`, `build.gradle` (Java)
  - `go.mod` (Go)
  - `Cargo.toml` (Rust)
  - `Gemfile`, `Gemfile.lock` (Ruby)
  - `Dockerfile`, `docker-compose.yml` (Containerization)
  - `.terraform`, `*.tf` (Terraform)

**2. Deep Analysis**
- Read 2-3 representative source files (e.g., `src/main...`, `app/routes...`, `controllers/...`).
- **Extract**:
  - **Coding Style**: Indentation (Tabs/Spaces), Naming (Camel/Snake), Semicolons?
  - **Architecture**: MVC? Hexagonal? Flat? Service-based? Write it as one Architecture Shape line.
  - **Testing**: Is there a `tests/` or `spec/` folder? Which framework is used?
  - **Patterns**: Repository pattern? Dependency injection? Service objects?

**3. Check Existing Stacks**
- **Action**: List all directories in `stacks/`
- **Compare**: Match detected stack against existing ones based on language + framework
  - Example: If detected "Python + FastAPI", check if `stacks/python-fastapi/` exists
  - Example: If detected "Node.js + Express", check if `stacks/node-express/` exists
  - Example: If detected "Ruby + Rails", check if `stacks/ruby-rails/` exists

**4A. If Match Found (Stack Already Exists)**
- **Action**: Use the existing stack
- **Steps**:
  1. Take the Architecture Shape from `stacks/{matched-name}/context.md` → `## Architecture Shape` (first non-empty line).
  2. Copy `stacks/{matched-name}/rules/*.mdc` → `.cursor/rules/<role>/stack-<file>.mdc` (scoping per step 9).
  3. **Brownfield note**: add to the top of each copied rule body: "Detected from existing codebase. Rules apply to new code only (Strictness: Low)."
  4. Inform user: "Detected {stack-name}! Using existing stack configuration from `stacks/{matched-name}/`"
  5. Go to step 10.

**4B. If No Match Found (New Stack Detected)**
- **Action**: Generate a clean stack name
  - Example: "Python + Flask" → `flask` or `python-flask`
  - Example: "React + AppFabric" → `react-appfabric`
  - Example: "Ruby + Rails" → `ruby-rails`
  - **Rule**: Use lowercase, hyphen-separated, no "detected-" prefix

**5. Present Detection Results**
- Show the user what was detected:
  ```
  Detected Stack (for <role>, scanned <scan root>):
  - Language: {Language + Version}
  - Framework: {Framework}
  - Architecture: {Pattern}
  - Testing: {Test Framework}
  - Style: {Naming Convention}
  ```

**6. Ask User for Reusability**
- **Question**: "Would you like to save this as a reusable stack in `stacks/{clean-name}/` for future projects?"
- **Options**:
  - **Yes** → Create complete reusable stack (go to step 7)
  - **No** → Create rules for this persona only (go to step 9, generating the rules in step 8b content directly into `.cursor/rules/<role>/`; do NOT create `stacks/{clean-name}/`)

**7. Create Reusable Stack Structure (If User Says Yes)**
- **Action**: Create the following directory structure:
  ```
  stacks/{clean-name}/
  ├── context.md
  ├── rules/
  ├── templates/
  └── examples/
  ```

**8. Generate Stack Content**

**8a. Create `stacks/{clean-name}/context.md`**
- **Format**:
  ```markdown
  # Project Context: {Detected Name}

  ## Architecture Shape
  {One line describing the detected shape}

  ## Tech Stack
  - Language: {Detected Language + Version}
  - Framework: {Detected Framework}
  - Database: {Detected Database}
  - Testing: {Detected Test Framework}
  - Linting: {Detected Linter}

  ## Detected Style
  - Coding Style: {Detected Naming Convention}
  - Architecture: {Detected Pattern}
  - Indentation: {Tabs or Spaces}

  ## Key Rules
  - {Core Rule 1 based on observed patterns}
  - {Core Rule 2 based on observed patterns}
  - {Core Rule 3 based on observed patterns}

  ## Strictness: Low
  - Refactoring: Only touch what is necessary
  - New Code: Apply full standards to new features only
  - Legacy Code: Document issues but don't force refactoring
  ```

**8b. Create `stacks/{clean-name}/rules/`**
- **Generate rules based on detected patterns**:
  - `100-style.mdc`: Coding standards based on observed code
  - `200-testing.mdc`: Testing patterns based on detected test framework
  - `300-architecture.mdc`: Architectural patterns observed in codebase

- **Example rule (`100-style.mdc`)**:
  ```markdown
  ---
  description: {Framework} coding standards (detected from codebase)
  alwaysApply: true
  ---

  # {Framework} Style Guide

  ## Detected Patterns
  - Naming: {detected naming convention} (observed in {X}% of codebase)
  - Architecture: {detected architecture} (observed in directory structure)
  - Testing: {detected test framework} (found in tests/ or spec/ directory)

  ## Rules
  - {Rule 1 based on observed code}
  - {Rule 2 based on observed code}
  - {Rule 3 based on observed code}
  ```
  The library copy stays generic (`alwaysApply: true`); step 9 scopes it to the persona when installing.

**8c. Extract `stacks/{clean-name}/templates/`**
- **Copy actual configuration files from the scanned codebase**:
  - `.env.example` (if exists)
  - `docker-compose.yml` (if exists)
  - `Makefile` (if exists)
  - Package/dependency files:
    - `requirements.txt` or `pyproject.toml` (Python)
    - `package.json` (Node.js)
    - `Gemfile` (Ruby)
    - `pom.xml` or `build.gradle` (Java)
    - `go.mod` (Go)
  - Framework-specific config files:
    - `tsconfig.json`, `jest.config.js` (Node/TypeScript)
    - `pytest.ini`, `setup.py` (Python)
    - `config/database.yml` (Rails)

- **Example**:
  ```
  stacks/{clean-name}/templates/
  ├── .env.example           # Copied from scan root
  ├── docker-compose.yml     # Copied from scan root
  ├── requirements.txt       # Copied from scan root
  └── pytest.ini             # Copied from scan root
  ```

**8d. Extract `stacks/{clean-name}/examples/`**
- **Copy exact code snippets from the codebase as reference examples**:
  - Find representative files (controllers, models, services, repositories)
  - Create example folders preserving the actual patterns
  - Use the ACTUAL code from the repo, not generic examples

- **Example Structure**:
  ```
  stacks/{clean-name}/examples/
  ├── crud-example/
  │   ├── controller.{ext}    # Actual controller file from repo
  │   ├── model.{ext}         # Actual model file from repo
  │   ├── service.{ext}       # Actual service file from repo
  │   └── test.{ext}          # Actual test file from repo
  └── auth-example/
      └── ...                 # If authentication exists in repo
  ```

- **How to extract**:
  1. Identify representative files (e.g., `app/controllers/users_controller.rb`)
  2. Create corresponding example folder (e.g., `examples/crud-example/`)
  3. Copy the file preserving the exact code: `users_controller.rb`
  4. This ensures future users get the SAME patterns found in the original codebase

**9. Install for the persona**
- Copy each rule (from `stacks/{name}/rules/*.mdc`, or the generated rules in context-only mode) → `.cursor/rules/<role>/stack-<file>.mdc`, rewriting the frontmatter to:
  ```
  ---
  description: <keep original description>
  globs: workspaces/<role>/**
  alwaysApply: false
  ---
  ```
  The `stack-` prefix keeps stack rules apart from the persona's own rules in the same folder (same as `/setup-stack`).
- Templates and examples stay in `stacks/` (the student's code is already in the workspace). Do not copy anything into `workspaces/<role>/`.
- **Never overwrite `.cursor/context.md`.** In the `## Persona: <role>` block set only:
  ```
  Stack: <stack name>
  Architecture Shape: <shape line>
  Active Phase: Phase 0 (Skeleton)
  ```
  Do not touch `## Active Personas` or other persona blocks.

**10. Write the stack manifest**

`.cursor/stacks/<role>.manifest.json` (same format as `/setup-stack`, so `/undo stack <role>` works):

```json
{
  "persona": "<role>",
  "stack": "<stack name>",
  "architecture_shape": "<shape>",
  "installed_at": "<ISO 8601>",
  "reconcile_mode": "detected",
  "scanned_path": "<scan root>",
  "files": [".cursor/rules/<role>/stack-100-style.mdc", "..."]
}
```

List only files written under `.cursor/`. Files created under `stacks/{clean-name}/` are library content and are not removed by `/undo`.

**11. Confirm**
```
✅ Stack for <role>: <stack> (<shape>), detected from <scan root>
   Rules: .cursor/rules/<role>/stack-*.mdc  (apply to workspaces/<role>/** only)
   Saved to library: stacks/<clean-name>/   (only if you chose Yes in step 6)

Next: /architect <role> @exercises/<role>/<exercise>/README.md  (or a path to your own plan)
```
- Ask: "Does this configuration look correct?"

## Usage
`/detect-stack <role>`
-> *Picks the persona → Scans its workspace (or your path) → Checks existing stacks → Creates reusable stack if needed → Updates only that persona's block.*

## Error Messages

| Situation | Message |
|---|---|
| No active persona | "⚠️ No persona configured. Run `/set-persona add <role>` first, then `/detect-stack <role>`." |
| Role not active | "`<role>` is not active. Run `/set-persona add <role>` first." |
| Stack already set | "`<role>` already uses `<stack>`. Run `/undo stack <role>` first." |

## Notes
- Detected stacks use clean names without "detected-" prefix
- Templates and examples are extracted from the ACTUAL codebase, preserving real patterns
- `Strictness: Low` is always set for brownfield projects
- Future projects can reuse detected stacks via `/setup-stack`
