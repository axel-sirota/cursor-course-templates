---
description: Configure the project stack, rules, and context (Start Here)
---

# Setup Stack Command

This command configures the project's technology stack. It is persona-aware: it reads the active persona from CLAUDE.md and shows only the stacks relevant to that persona.

## Execution Flow

### Step 1: Read CLAUDE.md and Detect Active Persona

Read the project's `CLAUDE.md` file and extract the value of the `Active Persona:` field.

- If no `Active Persona:` field is found, respond:
  > "No persona configured. Run `/set-persona` first, then come back to `/setup-stack`."
  > Stop.

- If `Active Persona: pm`, respond:
  > "The PM persona does not use a tech stack. Stack setup is not required for PM work.
  >
  > Run `/start-session` to begin your session."
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

Data Engineering:
  2. python-spark           — Distributed Pipelines (PySpark + Delta Lake)
  3. python-dbt-snowflake   — Analytics Modeling (dbt Core + Snowflake/BigQuery)
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
- **data-scientist**: `python-datascience`, `python-spark`, `python-dbt-snowflake`

If the selection is **not** in the allowed list for the persona, respond:

> "That stack is not available for the {persona} persona. Please choose from the list above."

Repeat from Step 3.

### Step 5: Read Architecture Shape

Read `stacks/{selected-stack}/context.md` to extract the architecture shape (look for an `Architecture Shape` or `Architecture` heading or field). Use the summary line (e.g. "Layered REST API (Router → Service → Repository)").

If the context file does not exist or has no architecture field, use the default:
- engineer stacks: "Layered API"
- devops stacks: "Infrastructure as Code"
- data-scientist stacks: "Notebook / Pipeline"

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
- Copy `stacks/{selection}/context.md` to `CLAUDE.md` (overwrite).
- If `stacks/{selection}/vibe/` exists, copy to `vibe/` in project root.
- If `stacks/{selection}/templates/` exists, copy to `templates/` in project root.

### Step 7: Confirm

Respond:

> "Stack configured: **{stack-name}** ({Architecture Shape}).
>
> Run `/start-session` to begin your session."

---

## Persona → Stack Reference

| Persona | Allowed Stacks |
|---------|---------------|
| engineer | python-fastapi, go-gin, go-grpc, java-spring, node-express, node-nestjs |
| devops | devops-terraform, devops-ansible, devops-k8s-helm |
| data-scientist | python-datascience, python-spark, python-dbt-snowflake |
| pm | (none — no stack required) |

---

## Error Messages

| Situation | Message |
|-----------|---------|
| No persona in CLAUDE.md | "No persona configured. Run `/set-persona` first." |
| PM persona | "The PM persona does not use a tech stack. Run `/start-session` to begin." |
| Invalid stack for persona | "That stack is not available for the {persona} persona. Try again." |
