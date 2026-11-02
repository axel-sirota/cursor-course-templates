# PM Persona Pack

Turns raw notes into validated PRDs and INVEST stories with testable acceptance criteria, all as markdown in `workspaces/pm/`.

Install with `/set-persona add pm`, then `/setup-stack pm` (pm-prd-markdown) → `/architect pm` → `/start-session pm`. All paths below are relative to `workspaces/pm/`.

## What this pack adds

**Commands:**
- `/pm-validate`: Three Amigos critique on a PRD (dev feasibility, QA edge cases, structural gap analysis)
- `/pm-decompose`: break a validated PRD into dependency-ordered tickets for the issue tracker
- `/pm-report`: build a stakeholder status update from the markdown tickets (or from Jira, if you configured an Atlassian MCP)

**Subagents:**
- `dev-perspective`: technical feasibility critique (systems touched, race conditions, cost estimates)
- `qa-perspective`: edge case and testability analysis (unnamed scenarios, untestable criteria, suggested rewrites)
- `gap-detector`: structural PRD completeness check (goals, personas, INVEST stories, NFRs, rollout plan)

**Hooks** (installed to `.cursor/scripts/pm/`, scoped to `workspaces/pm/`):
- `afterFileEdit`: `invest-validator.sh` and `ac-format-check.sh` on markdown files in `prds/`, `stories/` and `docs/prds/`
- `stop`: `gap-detector.sh` prints an advisory to run `/pm-validate` before the next session

**MCP servers:** none. The course works fully in markdown. See `SETUP.md` for optional vendor MCP servers (Atlassian, GitHub, Notion) you can add on your own.

## How this pack pairs with `/setup-stack`

The PM stack is `pm-prd-markdown`. It sets the Architecture Shape to "PRD Workspace" and installs PRD structure, style and checking rules into `.cursor/rules/pm/` next to this pack's rules. Both apply only to files in `workspaces/pm/`.

## Prerequisites

See `SETUP.md` for the pre-class checklist and the smoke test.
