---
description: Generate a transition prompt for the next coding session
---

# Next Session Command

Wraps up the current work and generates a "Context Beacon" for the next time you work.

## Execution Flow

## Persona Detection (run first)

Read the active persona from context:
- Cursor: `.cursor/context.md` — look for `## Active Persona`
- Claude Code: `CLAUDE.md` — look for `## Active Persona`

If section missing or value is empty → **STOP**. Tell the user: "⚠️ No persona configured. Run **/set-persona** first." Do not proceed.

Branch to the appropriate preamble below, then continue with the standard execution flow.

### Persona Preambles

Before generating the transition doc, run the persona's quality-gate check. Then ask whether the user has used the persona's in-session commands — if a session ended without using any of them, that's usually a sign the session was unfocused. Surface it.

**engineer:**
- Check test status (run `test-runner` subagent if available).
- Advance `## Active Phase` in context if phase AC are met.
- Ask: "Did you use `/engineer-tasks` and `/engineer-implement` during this session?" If no, ask why — it usually means the session lacked TDD structure. Recommend `/code-review` before wrap-up.
- Generate transition doc with: session status, where stopped, next immediate step, files to load, which in-session commands to use next time.

**designer:**
- Prompt for screenshot comparison via `responsive-checker` if not yet done.
- Update Figma context doc if design changed.
- Ask: "Did you use `/designer-extract`, `/designer-compose`, or `/designer-iterate` this session?" Recommend `/designer-handoff` if components are ready for dev.
- Generate transition doc with: components changed, open style questions, next frame to implement, which in-session commands to use next time.

**pm:**
- Run `gap-detector` on active PRD if not yet run this session.
- Update story count in context.
- Ask: "Did you use `/pm-decompose` or `/pm-validate`?" If validation has never run on the active PRD, run `/pm-validate` now.
- Generate transition doc with: stories validated, stories remaining, next three to work on, which in-session commands to use next time.

**data-scientist:**
- Invoke `experiment-tracker` to log session results if not yet done.
- Update experiment log summary in context.
- Ask: "Did you use `/ds-explore`, `/ds-experiment`, or `/ds-validate`?" If an experiment ran but `/ds-validate` hasn't, run it before wrap-up (seeds, leakage, baselines).
- Generate transition doc with: hypothesis tested, metrics achieved, next experiment to run, which in-session commands to use next time.

**devops:**
- Check whether `terraform plan` / `ansible-lint` / `helm lint` was run this session.
- Generate transition doc with: change scope, plan output (if any), apply status, next infra change to make.

---

**1. Analyze Session**
- What files were changed?
- What tests are passing?
- What is pending?

**2. Update Context**
- If `CLAUDE.md` tracks "Active Phase", suggest updating it if the phase is complete.

**3. Generate Transition Prompt**

Output a code block the user can copy-paste (or save to a file). Fill in the persona-specific block from the table below — DO NOT emit a generic template; the next-time commands change per persona.

```markdown
# Session Transition
**Last Status**: [Success/Fail]
**Stopped At**: [Function/File being worked on]
**Next Step**: [Immediate action for next session]

**Context to Load**:
- CLAUDE.md
- [Relevant Source File]

**Next pipeline command**: `/start-session` (continues the session loop).
Switch to `/architect` instead only if {Active Phase} just completed and you are starting a new phase.

**In-session commands for next time** ({Active Persona}):
{persona-specific block — see table below}
```

Persona-specific block to inline above (pick the row matching `## Active Persona`):

| Persona | In-session commands block |
|---|---|
| engineer | `- /engineer-tasks — decompose the next session goal into TDD-ordered tasks`<br>`- /engineer-implement — drive red→green→refactor for one task at a time`<br>`- /code-review and /research as needed` |
| designer | `- /designer-extract — pull design tokens from Figma`<br>`- /designer-compose — assemble new components from tokens`<br>`- /designer-iterate — apply review feedback`<br>`- /designer-handoff — produce dev-ready spec (when components are ready)` |
| pm | `- /pm-decompose — split a PRD epic into INVEST stories`<br>`- /pm-validate — check stories meet INVEST + have ACs`<br>`- /pm-report — produce a sprint status summary` |
| data-scientist | `- /ds-explore — EDA pass on a dataset`<br>`- /ds-experiment — run a single trained-model experiment with tracked metrics`<br>`- /ds-validate — sanity-check results (seeds, leakage, baselines)`<br>`- /ds-handoff — model card + serving spec` |
| devops | `- (no persona-specific commands yet) — use /code-review and /research, plus direct shell tools (terraform plan, ansible-lint, helm lint)` |

## Usage
`/next-session`
-> *Generates summary and next steps.*
