---
description: Configure the project stack, rules, and context (Start Here)
---

# Setup Stack Command

This command configures the project's technology stack. It is persona-aware: it reads the active persona from CLAUDE.md and shows only the stacks relevant to that persona.

## Execution Flow

### Step 1: Read CLAUDE.md and Detect Active Persona

Read the project's `CLAUDE.md` file and extract the value of the `Active Persona:` field.

- If no `Active Persona:` field is found, respond:
  > "⚠️ No persona configured. Run `/set-persona` first, then come back to `/setup-stack`."
  > Stop.

- If `Active Persona: pm` or `Active Persona: designer`, respond:
  > "The {persona} persona does not use a tech stack. Stack setup is not required.
  >
  > Next: run `/architect` to design your work, then `/start-session` to execute it."
  > Stop.

### Step 2: Show Persona-Filtered Stack Options

Display the stack list that matches the active persona:

---

**If Active Persona: engineer** — show:

```
Available stacks for Engineer persona:

Backend APIs:
  1. python-fastapi     — Python REST API (FastAPI + SQLAlchemy + Alembic)
  2. go-gin             — Go REST API (Gin + sqlx + testify)
  3. go-grpc            — Go gRPC Service (Protocol Buffers + buf)
  4. java-spring        — Java REST API (Spring Boot 3 + JPA + Testcontainers)
  5. node-express       — Node.js REST API (Express + TypeScript + Zod)
  6. node-nestjs        — Node.js Enterprise API (NestJS + TypeORM + Swagger)
```

---

**If Active Persona: devops** — show:

```
Available stacks for DevOps persona:

Infrastructure & Configuration:
  1. devops-terraform       — Cloud Infrastructure (Terraform + tflint + checkov)
  2. devops-ansible         — Configuration Management (Ansible + Molecule)
  3. devops-k8s-helm        — Kubernetes GitOps (Helm + ArgoCD)
```

---

**If Active Persona: data-scientist** — show:

```
Available stacks for Data Scientist persona:

Analysis & Modeling:
  1. python-datascience     — Notebooks + ML (Jupyter + scikit-learn + MLflow)
  2. r-tidyverse            — Statistical Computing (R + tidymodels + Quarto + Plumber)
  3. python-mlops           — MLOps Pipeline (MLflow + FastAPI serving + Pandera)

Data Engineering:
  4. python-spark           — Distributed Pipelines (PySpark + Delta Lake)
  5. python-dbt-snowflake   — Analytics Modeling (dbt Core + Snowflake/BigQuery)
```

---

### Step 3: Ask for Selection

Prompt the user:

> "Which stack? Enter the number or stack name:"

Wait for user input.

### Step 4: Validate Selection

Check that the selected stack is in the allowed list for the active persona:

- **engineer**: `python-fastapi`, `go-gin`, `go-grpc`, `java-spring`, `node-express`, `node-nestjs`
- **devops**: `devops-terraform`, `devops-ansible`, `devops-k8s-helm`
- **data-scientist**: `python-datascience`, `python-spark`, `python-dbt-snowflake`, `r-tidyverse`, `python-mlops`

If the selection is **not** in the allowed list for the persona, respond:

> "That stack is not available for the {persona} persona. You have three options:
>
>   1. Choose a different stack from the list above.
>   2. Type `new` to create a custom stack — I'll walk you through scaffolding `stacks/<your-name>/` from `stacks/blank/` (rules, templates, examples, context.md). Use this when none of the listed stacks fit your language/framework.
>   3. Type `cancel` to abort.
>
> Which would you like?"

- If user picks option 1: repeat from Step 3.
- If user picks option 2 (`new`):
  - Ask for a stack name (lowercase, hyphen-separated, e.g. `python-flask`, `ruby-rails`).
  - Copy `stacks/blank/` to `stacks/{new-name}/`.
  - Create the standard subdirs: `rules/`, `templates/`, `examples/`.
  - Open the new `stacks/{new-name}/context.md` and prompt the user to fill in language, framework, database, testing framework, key rules.
  - Once filled in, treat `{new-name}` as the selected stack and continue with Step 5.
- If user picks option 3 (`cancel`): stop.

### Step 5: Read Architecture Shape

Read `stacks/{selected-stack}/context.md` to extract the architecture shape (look for an `Architecture Shape` or `Architecture` heading or field). Use the summary line (e.g. "Layered REST API (Router → Service → Repository)").

If the context file does not exist or has no architecture field, use the default:
- engineer stacks: "Layered API"
- devops stacks: "Infrastructure as Code"
- data-scientist stacks: "Notebook / Pipeline"

### Step 5.5: Reconcile with Existing Code

Before copying any stack assets, check whether the project already contains code in the stack's language. This prevents blindly overwriting an existing project's structure.

**5.5a. Detect existing code:**

Use `Glob` (or equivalent) to find files matching the stack's primary language:

| Stack family | Glob pattern(s) |
|---|---|
| `python-*` | `**/*.py` (excluding `.venv/`, `__pycache__/`, `.tox/`) |
| `node-*` | `**/*.{js,ts,jsx,tsx}` (excluding `node_modules/`, `dist/`, `build/`) |
| `go-*` | `**/*.go` (excluding `vendor/`) |
| `java-spring` | `**/*.java` (excluding `target/`, `build/`) |
| `r-tidyverse` | `**/*.R` or `**/*.Rmd` |
| `devops-terraform` | `**/*.tf` |
| `devops-ansible` | `**/*.{yml,yaml}` under `playbooks/`, `roles/` |
| `devops-k8s-helm` | `**/Chart.yaml`, `**/values.yaml` |

Skip dotfiles (`.claude/`, `.cursor/`, `.git/`), the `stacks/` template library, and the `materials/` directory — those are template scaffolding, not user code.

**5.5b. If NO existing code is found:** print `"No existing code detected — clean install."` and proceed to Step 6 with no prompt.

**5.5c. If existing code IS found:** summarize what exists (be specific):

```
Existing code detected in this repo:
  • {N} files matching {pattern} (e.g. "12 .py files under src/")
  • Top-level dirs: {list, e.g. "src/, tests/, app/"}
  • Notable framework markers: {detected, e.g. "FastAPI import in src/main.py", "pytest in tests/conftest.py", "pyproject.toml"}
```

Then read `stacks/{selection}/context.md` and extract the "Key Rules" / "Vibe & Style" sections. Show them as the **recommended patterns** for this stack:

```
The {stack-name} stack recommends these patterns:
  • {pattern 1 from context.md}
  • {pattern 2}
  • {pattern 3}
```

**5.5d. Prompt the user:**

```
How should I handle the templates and rules?

  (a) Overwrite — copy stack templates/examples on top of existing code.
      Use this if your existing code is exploratory and you want the stack's
      canonical layout to take over.

  (b) Skip templates/examples — install only rules/ and context, do NOT
      copy templates/ or examples/. Use this if your existing code already
      follows the stack's patterns and you just want the AI to know the rules.

  (c) Merge — I'll diff each template file against your existing tree and
      ask per-file whether to overwrite, skip, or rename-with-suffix. Slowest
      but safest.

Which option? (a/b/c)
```

**5.5e. Honor the user's choice in Step 6:**

- **Option (a)**: proceed with Step 6 as written (overwrite).
- **Option (b)**: in Step 6, skip the `templates/` and `examples/` copy lines. Still copy `rules/` and write CLAUDE.md fields.
- **Option (c)**: for each file in `stacks/{selection}/templates/` (and `examples/`), check whether a same-named file exists in the project's `templates/` (or `examples/`). If yes, ask the user: "{path} exists. Overwrite, skip, or rename to {path}.from-stack?" Apply per-file. Record per-file decisions in the manifest.

Record the chosen mode (`overwrite` | `skip-templates` | `merge`) in the stack manifest (Step 6).

### Step 6: Write Stack Config to CLAUDE.md

Write (or update) the following fields in the project's `CLAUDE.md`. If sections already exist, replace their content. If they do not exist, append them.

```markdown
## Active Stack
{stack-name}

## Architecture Shape
{shape from stack's context.md}

## Active Phase
Phase 0 (Skeleton)
```

Also copy stack assets:
- Copy `stacks/{selection}/rules/*` to `.claude/rules/` (overwrite existing).
- If `stacks/{selection}/templates/` exists, copy to `templates/` in project root.
- If `stacks/{selection}/examples/` exists, copy to `examples/` in project root.

**Do NOT overwrite CLAUDE.md** — the fields written above must be preserved.

Track every file written in this step (rules, templates, examples, and the CLAUDE.md sections you modified) in a list. After all copies complete, write `.claude/.stack-manifest.json`:

```json
{
  "stack": "{selection}",
  "architecture_shape": "{shape}",
  "installed_at": "{ISO 8601 timestamp}",
  "reconcile_mode": "overwrite | skip-templates | merge | clean-install",
  "files": [
    ".claude/rules/000-...",
    "templates/...",
    "examples/...",
    "... every path written or overwritten in Step 6 ..."
  ],
  "claude_md_sections": ["Active Stack", "Architecture Shape", "Active Phase"]
}
```

`reconcile_mode` is `clean-install` when Step 5.5 found no existing code, or one of `overwrite | skip-templates | merge` when the user picked an option.

This manifest is required by `/undo stack` to cleanly reverse the install.

### Step 7: Confirm

Respond:

> "Stack configured: **{stack-name}** ({Architecture Shape}).
>
> Next: run `/architect` to design your application's phases and session plan, then `/start-session` to begin executing the first session."

(Never recommend `/start-session` directly after `/setup-stack` — the architect step is mandatory in the SDD pipeline. `/start-session` runs against an existing plan; without `/architect` there is no plan to start.)

---

## Persona → Stack Reference

| Persona | Allowed Stacks |
|---------|---------------|
| engineer | python-fastapi, go-gin, go-grpc, java-spring, node-express, node-nestjs |
| devops | devops-terraform, devops-ansible, devops-k8s-helm |
| data-scientist | python-datascience, python-spark, python-dbt-snowflake, r-tidyverse, python-mlops |
| pm | (none — no stack required) |

---

## Error Messages

| Situation | Message |
|-----------|---------|
| No persona in CLAUDE.md | "⚠️ No persona configured. Run `/set-persona` first." (mandatory — no fallback) |
| PM or designer persona | "The {persona} persona does not use a tech stack. Run `/architect` to design your work, then `/start-session`." |
| Invalid stack for persona | "That stack is not available for the {persona} persona. Choose from the list, type `new` to create one, or `cancel`." |
