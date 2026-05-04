# Session 13 — Persona-Aware `setup-stack` Command

**Phase:** 4 — Polish
**Parallel with:** nothing (depends on sessions 1–12 all complete)
**Depends on:** All stacks exist and are complete
**Client fit:** All personas — this is the entry-point UX fix

## Goal
The `setup-stack` command currently lists ALL stacks to everyone. An engineer sees Ansible and Spark. A data scientist sees go-gin and Java Spring. Fix it: filter stack options by active persona. Update QUICKSTART.md and student_runbook.md to reflect the 3-step flow.

---

## Files to Create / Update

```
.cursor/commands/
└── setup-stack.md          ← UPDATE (add persona detection + filtered stack lists)

.claude/commands/
└── setup-stack.md          ← UPDATE (identical to .cursor version)

QUICKSTART.md               ← UPDATE (Step 2 now shows persona-specific stack options)
student_runbook.md          ← UPDATE (per-persona setup-stack instructions)
```

---

## File Specifications

### `.cursor/commands/setup-stack.md` and `.claude/commands/setup-stack.md` (UPDATE)

Replace the current command with a persona-aware version. The command must:

1. **Read CLAUDE.md** to detect the active persona (look for `Active Persona:` field).
2. **If no persona set**: tell the user to run `/set-persona` first. Stop.
3. **Show persona-filtered stack options** (see below).
4. **Accept user selection** and write the stack config to CLAUDE.md.
5. **Confirm**: "Stack configured: {stack}. Run `/start-session` to begin."

#### Persona → Stack Mapping

**engineer:**
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

**devops:**
```
Available stacks for DevOps persona:

Infrastructure & Configuration:
  1. devops-terraform       — Cloud Infrastructure (Terraform + tflint + checkov)
  2. devops-ansible         — Configuration Management (Ansible + Molecule)
  3. devops-k8s-helm        — Kubernetes GitOps (Helm + ArgoCD)
```

**data-scientist:**
```
Available stacks for Data Scientist persona:

Analysis & Modeling:
  1. python-datascience     — Notebooks + ML (Jupyter + scikit-learn + MLflow)

Data Engineering:
  2. python-spark           — Distributed Pipelines (PySpark + Delta Lake)
  3. python-dbt-snowflake   — Analytics Modeling (dbt Core + Snowflake/BigQuery)
```

**pm:**
```
The PM persona does not use a tech stack.
Stack setup is not required for PM work.

Run `/start-session` to begin your session.
```

#### CLAUDE.md Fields to Write

When a stack is selected, write (or update) these fields in the project's CLAUDE.md:

```markdown
## Active Stack
{stack-name}

## Architecture Shape
{shape from stack's context.md}

## Active Phase
Phase 0 (Skeleton)
```

#### Full Command Flow (pseudocode for AI to follow)

```
1. Read CLAUDE.md
2. Extract "Active Persona:" value
3. IF persona not set:
     → "No persona configured. Run /set-persona first."
     → STOP
4. IF persona == "pm":
     → "PM persona does not use a stack. Run /start-session to begin."
     → STOP
5. Display persona-filtered stack list (see above)
6. Ask: "Which stack? Enter number or name:"
7. Wait for user input
8. Validate input is in allowed list for this persona
9. IF invalid: "That stack is not available for the {persona} persona. Try again."
10. Write Active Stack + Architecture Shape + Active Phase to CLAUDE.md
11. Confirm: "Stack configured: {stack-name} ({Architecture Shape}). Run /start-session to begin."
```

### `QUICKSTART.md` (UPDATE)

Update Step 2 to show persona-specific examples. Replace the current generic "run setup-stack" with:

```markdown
## Step 2: Choose Your Stack (Engineers and Data Scientists only)

Run `/setup-stack`. You'll see options filtered for your persona:

**Engineer** example:
```
Available stacks for Engineer persona:
  1. python-fastapi  — Python REST API
  2. go-gin          — Go REST API
  3. go-grpc         — Go gRPC Service
  4. java-spring     — Java REST API
  5. node-express    — Node.js REST API
  6. node-nestjs     — Node.js Enterprise API
```

**Data Scientist** example:
```
Available stacks for Data Scientist persona:
  1. python-datascience    — Notebooks + ML
  2. python-spark          — Distributed Pipelines
  3. python-dbt-snowflake  — Analytics Modeling
```

**DevOps** example:
```
Available stacks for DevOps persona:
  1. devops-terraform    — Cloud Infrastructure
  2. devops-ansible      — Configuration Management
  3. devops-k8s-helm     — Kubernetes GitOps
```

**PM**: Skip this step. PMs do not configure a stack.

## Step 3: Start Your Session

Run `/start-session`. The AI loads your persona + stack context and asks for your session goal.
```

### `student_runbook.md` (UPDATE)

Add a "Stack Selection" section to each persona's runbook entry. Show the specific stack options for that persona and note which stacks map to which client types:

- **Engineer → go-grpc**: for Intuit internal services
- **Engineer → node-nestjs**: for Salesforce/Travelers enterprise Node
- **Engineer → java-spring**: for Salesforce/Travelers Java
- **Data Scientist → python-spark**: for Databricks / large-scale ML
- **Data Scientist → python-dbt-snowflake**: for analytics engineering / Snowflake teams
- **DevOps → devops-ansible**: for server config management post-Terraform
- **DevOps → devops-k8s-helm**: for Kubernetes production deployments

---

## Acceptance Criteria

- [ ] `.cursor/commands/setup-stack.md` contains "Active Persona:" detection logic
- [ ] `.claude/commands/setup-stack.md` is identical to .cursor version
- [ ] Engineer persona sees 6 stacks (python-fastapi, go-gin, go-grpc, java-spring, node-express, node-nestjs)
- [ ] DevOps persona sees 3 stacks (devops-terraform, devops-ansible, devops-k8s-helm)
- [ ] Data Scientist persona sees 3 stacks (python-datascience, python-spark, python-dbt-snowflake)
- [ ] PM persona gets "no stack needed" message
- [ ] QUICKSTART.md Step 2 shows persona-specific examples
- [ ] student_runbook.md maps stacks to client types
- [ ] CLAUDE.md fields written: `Active Stack`, `Architecture Shape`, `Active Phase`
- [ ] Invalid stack selection (engineer trying to select devops-terraform) shows error message
