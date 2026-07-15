---
description: Perform comprehensive code review based on active stack rules
---

# Code Review Command

Perform a systematic review of the codebase. This command adapts its checks based on the detected language and framework in `CLAUDE.md`.

## Review Checklist

**1. Context Load**
- Read `CLAUDE.md` to identify the **Strictness Level** and **Stack**.
- Read `.claude/rules/*.md` to load the style guide.
- Identify the active stack's manifest file(s), test-file convention, and any dependency-vulnerability tool it declares (from the stack's rules or `CLAUDE.md`) so Sections 2-4 below can be applied to the correct ecosystem instead of assuming Python/Node/Java/Go.

**2. Security Audit**
- **Secrets**: Check for hardcoded keys/tokens (Regex search).
- **Injection**: Check DB queries for raw string concatenation.
- **Dependencies**: Identify the active stack's manifest file(s) (e.g. `requirements.txt`/`pyproject.toml`, `package.json`, `go.mod`, `pom.xml`/`build.gradle`, Terraform provider/module version pins) and check for known-vulnerable or unpinned versions using whatever vulnerability tool is available for that ecosystem (e.g. `pip-audit`, `npm audit`, `govulncheck`, OWASP dependency-check, `tfsec`/`checkov`). If no manifest or scanner applies to this stack, note that and skip rather than defaulting to Python/Node checks.

**3. Style & Standards**
- **Naming**: Does code match the Active Rule (CamelCase vs Snake_case)?
- **Complexity**: Identify functions > 50 lines or deep nesting.
- **Type Safety / Correctness Contracts**: Check whether the active stack's type/contract mechanism is used appropriately for the code under review — e.g. Python type hints, TypeScript avoiding `any`, Go/Java interface usage, or for infra-as-code stacks (e.g. Terraform) whether variable blocks declare explicit `type` constraints and validation rules instead of accepting untyped input. If the active stack has no equivalent concept, skip this check rather than forcing an ill-fitting one.

**4. Testing Gaps**
- Verify critical paths have corresponding tests, using whatever test location/convention the active stack's rules declare (e.g. `tests/`, co-located `_test.go`/`_test.tf` files, or another convention specified in `.claude/rules`). If no convention is documented, check the repo's actual layout before assuming `tests/`.
- Check if tests are actually asserting values (not just running).

## Usage
`/code-review` -> *Runs the audit and outputs a report of violations and suggestions.*
