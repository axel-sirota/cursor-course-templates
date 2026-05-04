# PM Persona Pack

This pack adds PM-specific commands, subagents, hooks, MCP integrations, and rules to the Adaptive SDLC. It is installed by running `/set-persona pm`.

## What this pack adds

**Commands:**
- `/pm-validate` — Three Amigos critique on a PRD: dev feasibility, QA edge cases, and structural gap analysis
- `/pm-decompose` — Break a validated PRD into dependency-ordered tickets for the issue tracker
- `/pm-report` — Pull live status from Jira or GitHub Issues and generate a stakeholder status update

**Subagents:**
- `dev-perspective` — Technical feasibility critique: systems touched, race conditions, cost estimates
- `qa-perspective` — Edge case and testability analysis: unnamed scenarios, untestable criteria, suggested rewrites
- `gap-detector` — Structural PRD completeness check: goals, personas, INVEST stories, NFRs, rollout plan

**Hooks:**
- `afterFileEdit` — Runs `invest-validator.sh` and `ac-format-check.sh` on markdown files in `prds/` and `docs/`
- `stop` — `gap-detector.sh` prints an advisory to run `/pm-validate` before the next session

**MCP servers:**
- `atlassian` — Jira + Confluence operations (requires `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`, `CONFLUENCE_URL`)
- `github-issues` — GitHub issue operations (requires `GITHUB_PAT`)
- `slack` — Optional: status updates via Slack (requires `SLACK_BOT_TOKEN`)
- `notion` — Optional: documentation sync (requires `NOTION_API_KEY`)

## Why no `setup-stack`

PM work produces markdown artifacts and operates on external services (Jira, Confluence, GitHub). It is not tied to any programming language or framework. There is no stack to configure.

## Prerequisites

See `SETUP.md` for Atlassian credential setup, GitHub token generation, and the smoke test.
