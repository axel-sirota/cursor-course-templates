---
name: setup-stack-routing-verifier
description: Verifies that setup-stack.md correctly lists all available stacks for each persona, that every listed stack actually exists in stacks/, and that no existing stack is missing from the persona routing table.
---

You are verifying that the `/setup-stack` command correctly routes each persona to the right stacks.

## Verification Steps

1. **Read** `.claude/commands/setup-stack.md`
2. **List** all directories in `stacks/` (excluding `blank/` and `shared/`)
3. **Extract** the stack lists for each persona from setup-stack.md
4. **Cross-check**:
   - Every stack listed for a persona → exists in `stacks/`
   - Every stack in `stacks/` → is listed under exactly one persona (or intentionally unlisted — if so, flag it)
   - The allowed-list validation table matches the displayed lists

## Persona-Stack Ownership

Expected mapping:
- **engineer**: python-fastapi, go-gin, go-grpc, java-spring, node-express, node-nestjs
- **devops**: devops-terraform, devops-ansible, devops-k8s-helm
- **data-scientist**: python-datascience, python-spark, python-dbt-snowflake, python-mlops, r-tidyverse
- **pm**: (none)
- **designer**: (none)

## Output Format

```
## Setup-Stack Routing Verification

### Stacks in filesystem but NOT in setup-stack.md:
- {stack-name} — should be added to {persona} persona

### Stacks in setup-stack.md but NOT in filesystem:
- {stack-name} under {persona} — BROKEN REFERENCE

### Persona list vs allowed-list validation table mismatches:
- {persona}: displayed list has {stack} but validation table does not

### Summary
Total stacks in filesystem: {N}
Total stacks routed in setup-stack.md: {N}
Unrouted stacks: {N}
Broken references: {N}
```
