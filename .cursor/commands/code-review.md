---
description: Perform comprehensive code review based on active stack rules
---

# Code Review Command

Perform a systematic review of the codebase. This command adapts its checks based on the detected language and framework in `.cursor/context.md`.

## Review Checklist

**1. Context Load**
- Read `@.cursor/context.md` to identify the **Strictness Level** and **Stack**.
- Read `@.cursor/rules/*.mdc` to load the style guide.

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
`@code-review` -> *Runs the audit and outputs a report of violations and suggestions.*
