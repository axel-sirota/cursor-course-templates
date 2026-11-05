---
description: Perform comprehensive code review based on active stack rules
---

# Code Review Command

Perform a systematic review of one persona's workspace against that persona's rules and stack.

```
/code-review [<role>]
```

## Persona Detection (run first)

- Role: the argument, else `.cursor/.active-session`, else the only active persona in `.cursor/context.md` → `## Active Personas`, else ask.
- No active persona → "⚠️ No persona configured. Run `/set-persona add <role>` first." Stop.
- Review scope is `workspaces/<role>/` only. Rules are `.cursor/rules/<role>/*.mdc`. Stack is in the `## Persona: <role>` block.

## Persona Focus (from persona.yaml)

Read `personas/<role>/persona.yaml`:

- `review_focus`: the persona-specific things to check. Review every item and report each one with a verdict and evidence.
- `quality_gate`: run every agent named there (for example `test-runner`, `token-validator`, `gap-detector`, `tie-out-checker`) against the review scope, if it is installed in `.cursor/agents/`. Skip agents that are not installed and say so in the report. Agents that write records rather than check them (for example `experiment-tracker`) are not run during a review; list them as "not run (writes records)".
- Agents named inside `review_focus` items run the same way.

Never hardcode persona names or focus lists in this command. persona.yaml is the source.

---

## Review Checklist

**1. Context Load**
- Read the `## Persona: <role>` block in `.cursor/context.md` for **Stack** and **Architecture Shape**.
- Read `.cursor/rules/<role>/*.mdc` to load the style guide.

**2. Security Audit**
- **Secrets**: Check for hardcoded keys/tokens (Regex search).
- **Injection / Input Trust**: Check DB queries for raw string concatenation (web/DB stacks).
- **Dependencies**: Check for known vulnerable or unpinned versions using the stack's tool: pip-audit / pip check (Python), npm audit (Node), govulncheck (Go), renv::status() (R), dbt parse (dbt). Skip if not applicable to the stack.

**3. Style & Standards**
- **Naming**: Does code match the Active Rule (CamelCase vs Snake_case)?
- **Complexity**: Identify functions > 50 lines or deep nesting.
- **Type Safety**:
  - *Python*: Are type hints used?
  - *TS*: Is `any` used?
  - *Java/Go*: Are interfaces used correctly?
  - *R*: Are function arguments documented with roxygen2 `@param` type annotations?
  - *SQL/dbt*: Are column types cast explicitly in staging models (no implicit type coercion)?

**4. Testing Gaps**
- Verify critical paths have corresponding tests in `tests/`.
- Check if tests are actually asserting values (not just running).

Skip checklist items that do not apply to the persona's stack (a PRD workspace has no type hints).

## Report

1. `review_focus` results: one row per item, ✅ / ❌ with evidence.
2. Agent results: one row per `quality_gate` agent run.
3. Checklist violations and suggestions, grouped by severity.

## Usage
`@code-review` -> *Runs the audit and outputs a report of violations and suggestions.*
