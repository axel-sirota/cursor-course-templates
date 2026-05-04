# Stack Expansion Architecture

**Goal:** Bring all existing stacks from STUB → COMPLETE, add 6 new stacks, extract shared vibe infrastructure, make `setup-stack` persona-aware.

**Completeness standard for every stack:**
1. `context.md` — Tech Stack, Architecture Shape, Vibe & Style, Key Rules, Active Phase
2. `rules/` — minimum 4 `.mdc` files: `000-workflow`, `100-architecture`, `200-testing`, `300-style` + stack-specific extras
3. `templates/` — minimum 2 files: `{stack}-starter.md` + `phase-checklist.md`
4. `vibe/` — minimum 2 docs: `vibe_architecture.md` + reference to shared lifecycle
5. `examples/` — minimum 1 reference implementation

---

## Phases

### Phase 1 — Fix Existing Stacks (5 sessions, all parallel)
Sessions 1–5. Each is independent.

### Phase 2 — Shared Vibe Infrastructure (1 session, parallel with Phase 1)
Session 6. Creates `stacks/shared/`. Independent of Phase 1.

### Phase 3 — New Stacks (6 sessions, 3 parallel pairs, after Phase 1+2)
Sessions 7–12.
- Pair A: `go-grpc` + `node-nestjs` (engineer persona)
- Pair B: `devops-ansible` + `devops-k8s-helm` (devops persona)
- Pair C: `python-spark` + `python-dbt-snowflake` (data-scientist persona)

### Phase 4 — Persona-Aware setup-stack + Docs (1 session, after Phase 3)
Session 13.

---

## Parallel Execution Graph

```
Sessions 1–6 (all independent, run simultaneously):
  S1  fix devops-terraform
  S2  fix go-gin
  S3  fix java-spring
  S4  fix node-express
  S5  fix python-datascience
  S6  extract shared vibe
           │
           ▼ (all 6 done)
Sessions 7–12 (3 pairs, run simultaneously):
  S7  go-grpc          S8  node-nestjs
  S9  devops-ansible   S10 devops-k8s-helm
  S11 python-spark     S12 python-dbt-snowflake
           │
           ▼ (all 6 done)
Session 13  setup-stack persona-aware + docs
```

Critical path: any 1 from S1–S6 → any 1 from S7–S12 → S13 = 3 sessions minimum.

---

## New Stacks Summary

| Stack | Persona | Client fit | Architecture Shape |
|---|---|---|---|
| `go-grpc` | engineer | Intuit | gRPC Service |
| `node-nestjs` | engineer | Salesforce, Travelers | REST API (enterprise) |
| `devops-ansible` | devops | All clients | IaC Playbook |
| `devops-k8s-helm` | devops | Platform teams | GitOps Platform |
| `python-spark` | data-scientist | Databricks/enterprise | Data Pipeline |
| `python-dbt-snowflake` | data-scientist | Analytics engineers | Analytics Model |
