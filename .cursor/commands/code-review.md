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
- No active persona → "⚠️ No persona configured. Run `/set-persona` first." Stop.
- Review scope is `workspaces/<role>/` only. Rules are `.cursor/rules/<role>/*.mdc`. Stack is in the `## Persona: <role>` block.

Use the matching preamble below, then the checklist.

### Persona Preambles

**engineer:** Security (secret leaks, injection), style (naming, types), testing (coverage, assertion quality). Use `code-reviewer` and `security-auditor` subagents if available.

**designer:** Token discipline (no hardcoded values), logic preservation (no handler/route/state changes), responsive behavior (breakpoints). Use `token-validator` subagent if available.

**pm:** INVEST compliance (all stories), Given/When/Then format (all ACs), NFR completeness. Use `gap-detector` subagent if available.

**data-scientist:** Reproducibility (seed set, requirements pinned, no absolute paths), experiment logging (all runs tracked), model card completeness. Use `reproducibility-checker` subagent if available.

**accountant:** Tie-outs (every reported number traces to a source file and row), no hardcoded amounts, `data/raw/` untouched, formulas visible, no personal data in outputs. Use `tie-out-checker` and `controls-checker` subagents if available.

---

## Review Checklist

**1. Context Load**
- Read the `## Persona: <role>` block in `.cursor/context.md` for **Stack** and **Architecture Shape**.
- Read `.cursor/rules/<role>/*.mdc` to load the style guide.

**2. Security Audit**
- **Secrets**: Check for hardcoded keys/tokens (Regex search).
- **Injection / Input Trust**: Check DB queries for raw string concatenation (web/DB stacks). Check template injection in Ansible (Jinja2), Helm (Go templates), and Terraform (string interpolation) where applicable.
- **Dependencies**: Check for known vulnerable or unpinned versions using the stack's tool: pip-audit / pip check (Python), npm audit (Node), govulncheck (Go), tflint + checkov (Terraform), renv::status() (R), dbt parse (dbt). Skip if not applicable to stack.

**3. Style & Standards**
- **Naming**: Does code match the Active Rule (CamelCase vs Snake_case)?
- **Complexity**: Identify functions > 50 lines or deep nesting.
- **Type Safety**:
  - *Python*: Are type hints used?
  - *TS*: Is `any` used?
  - *Java/Go*: Are interfaces used correctly?
  - *R*: Are function arguments documented with roxygen2 `@param` type annotations?
  - *SQL/dbt*: Are column types cast explicitly in staging models (no implicit type coercion)?
  - *Ansible*: Are variable types and allowed values documented in `defaults/main.yml` comments?

**4. Testing Gaps**
- Verify critical paths have corresponding tests in `tests/`.
- Check if tests are actually asserting values (not just running).

## Usage
`@code-review` -> *Runs the audit and outputs a report of violations and suggestions.*
