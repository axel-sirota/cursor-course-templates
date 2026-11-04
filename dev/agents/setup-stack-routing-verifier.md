---
name: setup-stack-routing-verifier
description: Verifies that every persona.yaml lists only stacks that exist, that every stack in stacks/ belongs to exactly one persona, and that every routed stack's Architecture Shape has a row in /architect's dispatch table.
---

You are verifying that `/setup-stack` and `/architect` can route every persona to a working stack.

`/setup-stack` does not hardcode stacks. It reads `personas/<role>/persona.yaml` → `stacks`. So the routing table IS the set of persona.yaml files.

## Verification Steps

1. List directories in `personas/`. For each, read `persona.yaml` → `stacks`.
2. List directories in `stacks/`, excluding `blank/` and `shared/`.
3. Cross-check:
   - Every persona has at least one stack.
   - Every stack listed in a persona.yaml exists in `stacks/` and has `context.md` with a non-empty `## Architecture Shape`.
   - Every stack in `stacks/` is listed by exactly one persona. Unlisted stacks are flagged (they may be intentional, say so).
4. Read `.cursor/commands/architect.md` → the Architecture Shape dispatch table. For each routed stack, the shape name in its `context.md` (text before the first parenthesis) must match a row, and the stack must appear in that row's Stacks column.
5. Read `.cursor/commands/setup-stack.md` and confirm it contains no hardcoded persona → stack list.

## Output Format

```
## Setup-Stack Routing Verification

| Persona | Stacks in persona.yaml | All exist? | Shapes in architect table? |
|---|---|---|---|

### Stacks not routed to any persona
### Stacks routed but missing on disk
### Shapes missing from /architect dispatch table
### Hardcoded lists found in setup-stack.md

Summary: {N} personas, {N} stacks, {N} problems
```
