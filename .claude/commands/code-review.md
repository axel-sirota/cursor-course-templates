---
description: Perform comprehensive code review based on active stack rules
---

# Code Review Command

Perform a systematic review of the codebase. This command adapts its checks based on the detected language and framework in `CLAUDE.md`.

## Persona Detection (run first)

Read the active persona from context:
- Cursor: `.cursor/context.md` — look for `## Active Persona`
- Claude Code: `CLAUDE.md` — look for `## Active Persona`

If section missing or value is empty → treat as `engineer` (backwards compatible default).

Branch to the appropriate preamble below, then continue with the standard execution flow.

### Persona Preambles

**engineer:** Security (secret leaks, injection), style (naming, types), testing (coverage, assertion quality). Use `code-reviewer` and `security-auditor` subagents if available.

**designer:** Token discipline (no hardcoded values), logic preservation (no handler/route/state changes), responsive behavior (breakpoints). Use `token-validator` subagent if available.

**pm:** INVEST compliance (all stories), Given/When/Then format (all ACs), NFR completeness. Use `gap-detector` subagent if available.

**data-scientist:** Reproducibility (seed set, requirements pinned, no absolute paths), experiment logging (all runs tracked), model card completeness. Use `reproducibility-checker` subagent if available.

---

## Review Checklist

**1. Context Load**
- Read `CLAUDE.md` to identify the **Strictness Level** and **Stack**.
- Read `.claude/rules/*.md` to load the style guide.

**2. Security Audit**
- **Secrets**: Check for hardcoded keys/tokens (Regex search).
- **Injection**: Check DB queries for raw string concatenation.
- **Dependencies**: Check if `requirements.txt`/`package.json` has known vulnerable versions (if `npm audit` or `pip-audit` is available).

**3. Style & Standards**
- **Naming**: Does code match the Active Rule (CamelCase vs Snake_case)?
- **Complexity**: Identify functions > 50 lines or deep nesting.
- **Type Safety**:
  - *Python*: Are type hints used?
  - *TS*: Is `any` used?
  - *Java/Go*: Are interfaces used correctly?

**4. Testing Gaps**
- Verify critical paths have corresponding tests in `tests/`.
- Check if tests are actually asserting values (not just running).

## Usage
`/code-review` -> *Runs the audit and outputs a report of violations and suggestions.*
