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
  - `.terraform`, `*.tf`, `versions.tf`, `backend.tf` (Terraform)
- **Fallback (if none of the above manifests are found)**:
  - Look for a single dominant file extension in the tree (heuristic language detection)
  - Look for a top-level `Makefile` or `justfile`
  - Look for `.ipynb` notebooks or `dags/`/`pipelines/` (data-pipeline)
  - Look for a static `index.html` / `public/` root with no server-side code (ui/static)
  - **Do not guess framework details** in this case. Record shape as `unknown` and ask the user to confirm what the project is before continuing to Step 2.

**2. Deep Analysis**
- Read 2-3 representative source files. Which files are representative depends on what Reconnaissance found — do not default to web-app paths:
  - **Web API / service**: `src/main...`, `app/routes...`, `controllers/...`
  - **Infra (Terraform/etc.)**: `main.tf`, `modules/*/main.tf`, `variables.tf`, `outputs.tf`
  - **UI / frontend-only**: `src/components/...`, `src/pages/...`, `styles/...`
  - **CLI**: `cmd/...`, `bin/...`, the entrypoint that does argument parsing
  - **Library**: the public API module (`index.ts`, `__init__.py`, `lib.rs`, etc.)
  - **Data pipeline**: `dags/...`, `pipelines/...`, `*.ipynb`, `notebooks/...`
- **Extract**:
  - **Coding Style**: Indentation (Tabs/Spaces), Naming (Camel/Snake), Semicolons?
  - **Architecture**: MVC? Hexagonal? Flat? Service-based? (For infra: root module vs. child modules. For UI: component/page structure. For CLI/library: package/module layout.)
  - **Testing**: Is there a `tests/` or `spec/` folder? Which framework is used? Include non-backend options: infra uses Terratest, `terraform validate`, or `checkov`; UI uses Playwright, Cypress, or React Testing Library.
  - **Patterns**: Repository pattern? Dependency injection? Service objects? (Only where applicable to the detected shape.)

**2B. Classify Architecture Shape**
- **Action**: Based on Reconnaissance + Deep Analysis, classify the project into exactly one shape:
  - `service` — has HTTP routes/handlers, listens on a port
  - `infra` — Terraform/CloudFormation/Pulumi/Ansible; provisions resources, no runtime app
  - `ui` — frontend/static site; components/pages, no backend routes
  - `cli` — single/multi command entrypoint, no server
  - `library` — exposes a public API/package for other code to import, no entrypoint app
  - `data-pipeline` — ETL/notebooks/DAGs
  - `unknown` — reconnaissance fell through to the fallback bullet and shape could not be determined; ask the user to confirm
- **Store this as `Architecture Shape`** — this is the same field name and vocabulary that `.cursor/context.md`'s `## Architecture Shape` section and `@setup-stack` use, so detect-stack output stays consistent with the rest of the pipeline.
- **Every subsequent step in this command branches on this shape** instead of assuming `service`.

**3. Check Existing Stacks**
- **Action**: List all directories in `stacks/`
- **Compare**: Match detected stack against existing ones based on language + framework (for `service`/`ui`) or language + tool (for `infra`/`cli`/`library`/`data-pipeline`)
  - Example: If detected "Python + FastAPI" (`service`), check if `stacks/python-fastapi/` exists
  - Example: If detected "Node.js + Express" (`service`), check if `stacks/node-express/` exists
  - Example: If detected "Ruby + Rails" (`service`), check if `stacks/ruby-rails/` exists
  - Example: If detected "Terraform + AWS" (`infra`), check if `stacks/devops-terraform/` exists

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
  - Example: "Python + Flask" (`service`) → `flask` or `python-flask`
  - Example: "React + AppFabric" (`ui`) → `react-appfabric`
  - Example: "Ruby + Rails" (`service`) → `ruby-rails`
  - Example: "Terraform + GCP" (`infra`) → `terraform-gcp`
  - Example: "Go CLI" (`cli`) → `go-cli`
  - **Rule**: Use lowercase, hyphen-separated, no "detected-" prefix

**5. Present Detection Results**
- Show the user what was detected. Fields shown depend on `Architecture Shape` (omit fields that don't apply — do not fill them with placeholders):
  ```
  Detected Stack:
  - Architecture Shape: {service | infra | ui | cli | library | data-pipeline | unknown}
  - Language: {Language + Version}
  - Framework / Tool: {Framework, or Provisioner/Tool for infra, or "N/A" only if truly none}
  - Architecture: {Pattern}
  - Testing: {Test Framework or infra/UI test tool}
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
- **Format**: Include only the fields relevant to the detected `Architecture Shape` from Step 2B. Never emit an empty or "N/A" placeholder line for a field that doesn't apply to the shape — omit the line entirely instead.
  - **`service`**: Language, Framework, Database, Testing, Linting
  - **`infra`**: Language (e.g. HCL), Provisioner/Tool (Terraform/Pulumi/CloudFormation), Cloud Provider, State Backend, Testing (validate/plan-check tool), Linting (tflint/checkov)
  - **`ui`**: Language, UI Framework, Build Tool, Testing, Linting
  - **`cli`** / **`library`**: Language, Package Manager, Testing, Linting (no Database, no Framework)
  - **`data-pipeline`**: Language, Orchestrator/Tool (Airflow/dbt/etc.), Testing, Linting

  ```markdown
  # Project Context: {Detected Name}

  ## Architecture Shape
  {service | infra | ui | cli | library | data-pipeline}

  ## Tech Stack
  {Only the fields applicable to the shape above, e.g.:}
  - Language: {Detected Language + Version}
  - Framework / Tool: {Detected Framework, or Provisioner for infra — omit if not applicable}
  - Database: {Detected Database — omit entirely for infra/ui/cli/library/data-pipeline unless one is genuinely used}
  - Testing: {Detected Test Framework or tool}
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
  - See `plan/PHASES.md` for current phase/session state (created by `@architect`). If `@architect` has not been run yet, no phase is active.
  ```

**8b. Create `stacks/{clean-name}/rules/`**
- **Generate rules based on detected patterns**:
  - `100-style.mdc`: Coding standards based on observed code
  - `200-testing.mdc`: Testing patterns based on detected test framework/tool
  - `300-architecture.mdc`: Architectural patterns observed in codebase

- **Example rule (`100-style.mdc`)**:
  ```markdown
  ---
  description: {Stack Name} coding standards (detected from codebase)
  alwaysApply: true
  ---

  # {Detected Shape} Style Guide — {Stack Name}

  ## Detected Patterns
  - Naming: {detected naming convention} (observed in {X}% of codebase)
  - Architecture: {detected architecture} (observed in directory structure)
  - Testing: {detected test framework or tool} (found in tests/ or spec/ directory)

  ## Rules
  - {Rule 1 based on observed code}
  - {Rule 2 based on observed code}
  - {Rule 3 based on observed code}
  ```
  - Use `{Detected Shape} Style Guide` (e.g. "Infra Style Guide", "CLI Style Guide") rather than assuming a web framework name exists — for `service`/`ui` stacks with a real framework, `{Stack Name}` naturally carries it (e.g. "python-fastapi").

**8c. Extract `stacks/{clean-name}/templates/`**
- **Copy actual configuration files from the detected codebase**. Which files are relevant depends on `Architecture Shape`:
  - **Always check for**: `.env.example`, `docker-compose.yml`, `Makefile` (if they exist in repo)
  - **`service`**: Package/dependency files — `requirements.txt`/`pyproject.toml` (Python), `package.json` (Node.js), `Gemfile` (Ruby), `pom.xml`/`build.gradle` (Java), `go.mod` (Go); plus framework config — `tsconfig.json`, `jest.config.js` (Node/TypeScript), `pytest.ini`, `setup.py` (Python), `config/database.yml` (Rails)
  - **`infra`**: `*.tf`, `versions.tf`, `backend.tf`, `*.tfvars.example`
  - **`ui`**: `package.json`, `vite.config.*`, `next.config.*`, component-library config
  - **`cli`** / **`library`**: build/packaging manifest only (Python/Node/Go/Rust/Java manifests above, as applicable — no framework config)
  - **`data-pipeline`**: `dbt_project.yml`, DAG config, `requirements.txt`/`pyproject.toml`

- **Example (`service` shape)**:
  ```
  stacks/{clean-name}/templates/
  ├── .env.example           # Copied from repo root
  ├── docker-compose.yml     # Copied from repo root
  ├── requirements.txt       # Copied from repo root
  └── pytest.ini             # Copied from repo root
  ```

- **Example (`infra` shape)**:
  ```
  stacks/{clean-name}/templates/
  ├── versions.tf             # Copied from repo root
  ├── backend.tf              # Copied from repo root
  └── terraform.tfvars.example # Copied from repo root
  ```

**8d. Extract `stacks/{clean-name}/examples/`**
- **Copy exact code snippets from the codebase as reference examples.** The representative example depends on `Architecture Shape`:
  - **`service`**: controller/model/service/test — find representative files (controllers, models, services, repositories)
  - **`infra`**: one representative module (`main.tf` + `variables.tf` + `outputs.tf`) as `module-example/`
  - **`ui`**: one representative component + its test as `component-example/`
  - **`cli`**: one representative command handler as `command-example/`
  - **`library`**: one public API entrypoint + its usage example as `api-example/`
  - **`data-pipeline`**: one representative DAG/pipeline + its test as `pipeline-example/`
  - Use the ACTUAL code from the repo, not generic examples

- **Example Structure (`service` shape)**:
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

- **Example Structure (`infra` shape)**:
  ```
  stacks/{clean-name}/examples/
  └── module-example/
      ├── main.tf              # Actual module from repo
      ├── variables.tf         # Actual module from repo
      └── outputs.tf           # Actual module from repo
  ```

- **How to extract**:
  1. Identify representative files for the detected shape (e.g., `app/controllers/users_controller.rb` for `service`; `modules/networking/main.tf` for `infra`)
  2. Create the corresponding example folder (e.g., `examples/crud-example/`, `examples/module-example/`)
  3. Copy the file preserving the exact code
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
  1. Generate `.cursor/context.md` with detected configuration (including `Architecture Shape`)
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
- If `Architecture Shape` was `unknown`, do not let this pass silently — confirm the shape with the user before finishing.

## Usage
`@detect-stack`
-> *Scans repo → Classifies Architecture Shape → Checks existing stacks → Creates reusable stack if needed → Adapts Agent to your Reality.*

## Notes
- Detected stacks use clean names without "detected-" prefix
- Templates and examples are extracted from the ACTUAL codebase, preserving real patterns
- `Strictness: Low` is always set for brownfield projects
- Future projects can reuse detected stacks via `@setup-stack`
- This command is stack-shape-agnostic: it works identically for `service`, `infra`, `ui`, `cli`, `library`, and `data-pipeline` projects — no step assumes a web application unless `Architecture Shape` is `service`
