---
description: Automatically detect stack, style, and structure of an existing project
---

# Detect Stack Command

This command analyzes an existing codebase (Brownfield) to generate a custom configuration. It is the "Universal Adapter" for unknown or legacy projects.

## Execution Flow

**1. Reconnaissance**
- **Action**: Scan the root directory and key subdirectories.
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
  - **Architecture**: MVC? Hexagonal? Flat? Service-based?
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
  1. Copy `stacks/{matched-name}/context.md` → `.cursor/context.md`
  2. Copy `stacks/{matched-name}/rules/*` → `.cursor/rules/`
  3. **Adjust context for brownfield**:
     - Set `Strictness: Low` (if not already set)
     - Add note: "Detected from existing codebase - rules apply to new code only"
  4. Inform user: "Detected {stack-name}! Using existing stack configuration from `stacks/{matched-name}/`"
  5. **Done** ✅

**4B. If No Match Found (New Stack Detected)**
- **Action**: Generate a clean stack name
  - Example: "Python + Flask" → `flask` or `python-flask`
  - Example: "React + AppFabric" → `react-appfabric`
  - Example: "Ruby + Rails" → `ruby-rails`
  - **Rule**: Use lowercase, hyphen-separated, no "detected-" prefix

**5. Present Detection Results**
- Show the user what was detected:
  ```
  Detected Stack:
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
  - **No** → Create context for this project only (go to step 10)

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

  ## Active Phase
  - Current: Phase 0 (Skeleton)
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

**8c. Extract `stacks/{clean-name}/templates/`**
- **Copy actual configuration files from the detected codebase**:
  - `.env.example` (if exists in repo)
  - `docker-compose.yml` (if exists in repo)
  - `Makefile` (if exists in repo)
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
  ├── .env.example           # Copied from repo root
  ├── docker-compose.yml     # Copied from repo root
  ├── requirements.txt       # Copied from repo root
  └── pytest.ini             # Copied from repo root
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

**9. Copy to Current Project**
- **Action**: Copy generated stack to `.cursor/` for immediate use
  1. Copy `stacks/{clean-name}/context.md` → `.cursor/context.md`
  2. Copy `stacks/{clean-name}/rules/*` → `.cursor/rules/`
  3. (Templates and examples stay in `stacks/` for future projects)

- **Inform User**:
  ```
  ✅ Stack saved to `stacks/{clean-name}/`
  ✅ Templates extracted from your config files
  ✅ Examples extracted from your codebase
  ✅ Context activated for this project

  Future projects can select '{clean-name}' from @setup-stack
  ```

**10. Context-Only Mode (If User Says No)**
- **Action**: Create context and rules for this project only (not reusable)
  1. Generate `.cursor/context.md` with detected configuration
  2. Generate `.cursor/rules/` with basic rules
  3. Set `Strictness: Low`
  4. **Do NOT** create `stacks/{clean-name}/`

- **Inform User**:
  ```
  ✅ Context configured for this project only

  To use standard stacks in future projects, run @setup-stack and select from the library
  ```

**11. Final Confirmation**
- Present the context to the user.
- Ask: "Does this configuration look correct? Ready to start working?"

## Usage
`@detect-stack`
-> *Scans repo → Checks existing stacks → Creates reusable stack if needed → Adapts Agent to your Reality.*

## Notes
- Detected stacks use clean names without "detected-" prefix
- Templates and examples are extracted from the ACTUAL codebase, preserving real patterns
- `Strictness: Low` is always set for brownfield projects
- Future projects can reuse detected stacks via `@setup-stack`
