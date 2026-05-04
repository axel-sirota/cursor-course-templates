# Session 14 — Phase J: Docs Part 2 (student_runbook + CLAUDE.md)

**Phase:** J (final)
**Goal:** Update student_runbook.md with per-persona flows. Update CLAUDE.md placeholder. Final acceptance test for the entire build.
**Depends on:** Session 13 complete
**Next session:** None — build complete

---

## Files to Update

```
student_runbook.md   ← ADD per-persona workflow sections
CLAUDE.md            ← UPDATE placeholder text
```

---

## Change Specifications

### `student_runbook.md`

Read current content first. Then add a **Per-Persona Workflows** section.

The section should have one subsection per persona, each following this structure:
- First command of the day
- Core workflow loop (what commands to use in sequence)
- When to use subagents (and which ones)
- What hooks will fire (so students know what to expect)
- Capstone connection (how this persona's output feeds the next)

**Engineer workflow:**
```
Start: /start-session
Plan:  /architect "feature description"
Tasks: /engineer-tasks
Build: /engineer-implement  (loops per task: red→green→refactor)
Check: /code-review
End:   /next-session

Subagents fired automatically by /engineer-implement:
  - test-runner (after each red and green step)
  - security-auditor (on tasks touching auth/DB/I-O)
  - verifier (before marking task done)
  - code-reviewer (before /code-review)

Hooks:
  - Every file edit → lint.sh + type-check.sh (advisory)
  - Every shell command → block-destructive.sh (blocking for dangerous patterns)
  - Session end → test-runner.sh

Capstone output: working code + passing tests satisfying PM's acceptance criteria
```

**Designer workflow:**
```
Start:   /start-session
Extract: /designer-extract {figma-url}
Build:   /designer-compose {figma-context-file}
Refine:  /designer-iterate  (interactive: click + describe)
Ship:    /designer-handoff
End:     /next-session

Subagents:
  - figma-extractor (invoked by /designer-extract)
  - token-validator (invoked by /code-review)
  - responsive-checker (invoked by /designer-handoff)

Hooks:
  - Every CSS/SCSS/TSX/JSX edit → token-validator.sh + no-inline-styles.sh (advisory)
  - Session end → screenshot-compare.sh (advisory prompt)

Capstone output: PR_DESCRIPTION.md + responsive screenshots showing prototype matching Figma
```

**PM workflow:**
```
Start:     /start-session
Draft:     /architect "feature or problem statement"
Validate:  /pm-validate  (Three Amigos critique)
Decompose: /pm-decompose
Track:     /pm-report  (after engineers are working)
End:       /next-session

Subagents fired by /pm-validate:
  - dev-perspective (technical feasibility)
  - qa-perspective  (edge cases + testability)
  - gap-detector    (structural PRD completeness)

Hooks:
  - Every PRD/spec markdown edit → invest-validator.sh + ac-format-check.sh (advisory)
  - Session end → gap-detector.sh (advisory prompt)

Capstone output: PRD with INVEST stories + Given/When/Then ACs + Jira tickets
```

**Data Scientist workflow:**
```
Start:      /start-session
Explore:    /ds-explore  (profile data, form hypotheses)
Experiment: /ds-experiment  (run model, log results)
Validate:   /ds-validate  (held-out test, bias check)
Ship:       /ds-handoff  (model card)
End:        /next-session

Subagents:
  - data-profiler (invoked by /ds-explore)
  - experiment-tracker (invoked by /ds-experiment and /next-session)
  - reproducibility-checker (invoked by /ds-validate)

Hooks:
  - Every .py/.ipynb edit → seed-check.sh + notebook-lint.sh (advisory)
  - Session end → log-experiment.sh (advisory prompt)

Capstone output: model card + validation report + reproducibility confirmation
```

### `CLAUDE.md`

Replace current placeholder content with:

```markdown
# Project Context

> ⚠️ No Persona Configured
>
> This project has not been configured yet.
>
> **Step 1:** Run `/set-persona` to choose your role:
> - `engineer` — software developer
> - `designer` — UI/UX designer
> - `pm` — product manager
> - `data-scientist` — data scientist / ML engineer
>
> **Step 2 (engineer + data-scientist only):** Run `/setup-stack` to choose your tech stack.
>
> **Step 3:** Run `/start-session` to begin working.
```

---

## Final Acceptance Test (Entire Build)

Run all of these before marking the build complete:

### Persona install tests
- [ ] `/set-persona engineer` → manifest written, files in `.cursor/` and `.claude/`, hooks reference correct paths per side
- [ ] `/set-persona designer` after engineer → engineer files removed, designer files installed, manifest updated
- [ ] `/set-persona pm` → clean switch from designer
- [ ] `/set-persona data-scientist` → clean switch from pm
- [ ] `/set-persona engineer` again → idempotent reinstall

### Stack test
- [ ] After `set-persona engineer`: `/setup-stack python-fastapi` → stack rules merge with engineer rules (no conflicts)
- [ ] After `set-persona data-scientist`: `/setup-stack python-datascience` → DS context loaded

### Client overlay test
- [ ] Create `client-config/` from `client-config-sample/`, add dummy `client-config/client.md` with `## Client: TestCorp`
- [ ] `/set-persona engineer` → confirmation shows "Client overlay: TestCorp"
- [ ] `CLAUDE.md` shows `## Active Client: TestCorp`
- [ ] `client-config/personas/engineer/mcp.json` → `.cursor/mcp.json` is client version, not base
- [ ] Delete `client-config/`, run `/set-persona engineer` → runs cleanly, no error about missing client config

### Universal command tests
- [ ] With `## Active Persona: designer` in context: `/architect` asks for component hierarchy, not API surface
- [ ] With `## Active Persona: pm` in context: `/code-review` checks INVEST + AC format
- [ ] With no persona set: `/start-session` falls back to engineer behavior

### Backwards compat test
- [ ] In a clean clone with no persona set: `/setup-stack python-fastapi` → works exactly as before (no persona system interference)

### Dual-tool symmetry test
- [ ] `diff .cursor/commands/set-persona.md .claude/commands/set-persona.md` → identical
- [ ] `diff .cursor/commands/architect.md .claude/commands/architect.md` → identical
- [ ] `diff .cursor/hooks.json .claude/hooks.json` → NOT identical (path difference expected)
- [ ] `cat .claude/hooks.json | grep ".cursor"` → empty (no `.cursor/` paths on Claude side)

### Docs test
- [ ] `README.md` has `set-persona` as first command in the table
- [ ] `QUICKSTART.md` starts with "Step 0"
- [ ] `METHODOLOGY.md` has `## Personas` section
- [ ] `student_runbook.md` has all 4 per-persona workflow sections
- [ ] `CLAUDE.md` has the new placeholder with 3-step instructions
