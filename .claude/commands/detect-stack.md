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
  - `Dockerfile`, `docker-compose.yml` (Containerization)
  - `.terraform`, `*.tf` (Terraform)

**2. Deep Analysis**
- Read 2-3 representative source files (e.g., `src/main...`, `app/routes...`).
- **Extract**:
  - **Coding Style**: Indentation (Tabs/Spaces), Naming (Camel/Snake), Semicolons?
  - **Architecture**: MVC? Hexagonal? Flat?
  - **Testing**: Is there a `tests/` folder? Which framework is used?

**3. Context Generation**
- Generate a **Custom** `CLAUDE.md` with the findings.
- **Critical**: Set `Strictness: Low` by default.
  - *Reasoning*: We don't want to enforce strict new rules on a legacy codebase immediately.
- **Format**:
  ```markdown
  # Project Context: {Detected Name}
  
  ## Tech Stack
  - Language: {Detected Language}
  - Framework: {Detected Framework}
  - Testing: {Detected Test Framework}
  
  ## Detected Style
  - Naming: {Detected Pattern}
  - Indentation: {Detected Pattern}
  
  ## Strictness: Low
  - Refactoring: Only touch what is necessary.
  - Verification: Run existing tests, do not force TDD on legacy code.
  ```

**4. Rule Generation (Optional)**
- If the stack is **totally unknown** (e.g., Perl), generate a generic `.claude/rules/style.md` based on the observed patterns.
- If the stack is **Known** (e.g., Python), copy the standard rules but append a "Legacy Override" section.

**5. Confirmation**
- Present the draft context to the user.
- Ask: "Does this look correct? Shall I activate this context?"

## Usage
`/detect-stack`
-> *Scans repo -> Generates Context -> Adapts Agent to your Reality.*

