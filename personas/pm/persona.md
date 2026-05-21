# PM Persona

## First 5 minutes

You have three possible starting points. Pick the one that matches what you have right now.

**(a) I have raw notes / a meeting transcript / a stakeholder ask**
Open Claude Code. Paste the notes. Ask: "Draft a PRD scaffold from these notes in `prds/draft-{name}.md` — include goals, non-goals, INVEST user stories, Given/When/Then AC, NFRs, edge cases." Iterate in markdown until the draft holds water.

**(b) I have a draft PRD in `prds/`**
```
/pm-validate prds/my-feature.md
```
Expect: a Three Amigos critique appended to the file (dev feasibility, QA edge cases, structural gap analysis). Resolve flagged items, re-run if needed.

**(c) I have a validated PRD ready for engineering**
```
/pm-decompose prds/my-feature.md
```
Expect: dependency-ordered tickets in `prds/my-feature-tickets.md`. Push to Jira / GitHub Issues via MCP when you're happy.

If you want a live status snapshot from Jira: `/pm-report`.

## Platform gotchas

- **PRDs live in `prds/*.md`. Jira / Confluence are push targets, not your editor.** You will spend most of your time in markdown files in the repo, not in the Jira UI.
- **Atlassian MCP needs the right token.** If `JIRA_API_TOKEN` is missing or scoped wrong, ticket creation fails silently. Smoke-test the MCP after install (ask Claude to "list my Jira projects").
- **Claude doesn't know your product unless you tell it.** Add a 5-line product summary to `CLAUDE.md` (target users, what the product does, key constraints). Generic PRDs come from generic context.
- **The terminal is just a text input.** If "open Claude Code in a terminal" feels foreign, that's expected. You will type ~3 commands per session, not learn shell scripting.

## What this pack does NOT do

- It does NOT write code for you. Use the engineer persona for that.
- It does NOT decide product strategy. It enforces structure on decisions you make.
- It does NOT replace stakeholder conversations. It captures their outcomes.
- It does NOT auto-push to Jira. You review tickets in markdown first, then push.

## How this relates to Anthropic's official PM plugin

Anthropic ships an official PM plugin (`knowledge-work-plugins/product-management`) with 14 commands and 11 skills covering the full PM lifecycle — `/write-spec`, `/roadmap-update`, `/stakeholder-update`, `/synthesize-research`, `/competitive-brief`, `/metrics-review`, etc.

**This pack is the teaching subset.** Three commands (`/pm-validate`, `/pm-decompose`, `/pm-report`) focused on the three highest-friction PM tasks. The goal is for you to learn the PRD-as-code workflow here, then adopt the full Anthropic plugin (or build your own) once the pattern clicks.

## What `/architect` produces for this persona

Run `/architect` after `/set-persona pm`. There is no `/setup-stack` for PM — output is **structured documentation**, not code:

- `plans/interface-contract.md` — PRD structure: goals, non-goals, user personas, INVEST user stories, NFR categories
- `plans/sessions/session-1-phase-0.md` — Discovery + Specify session (write the PRD)
- `plans/sessions/session-N-phase-X.md` — Validate session, Decompose session, etc.

No code is scaffolded. The "skeleton" is the PRD document tree.

---

## Mental Model

You ship clarity. Your unit of delivery is a PRD that engineering can build without guessing — with INVEST-compliant user stories, Given/When/Then acceptance criteria, explicit edge cases, and tickets decomposed and dependency-ordered so the sprint starts with confidence.

## Vocabulary

- **PRD** — Product Requirements Document: the authoritative description of what to build and why.
- **User story (INVEST)** — A story that is Independent, Negotiable, Valuable, Estimable, Small, and Testable.
- **Acceptance criteria (Given/When/Then)** — Machine-verifiable conditions that define "done" for each story.
- **Three Amigos** — A collaborative review with dev, QA, and PM perspectives before work begins.
- **Epic** — A collection of related stories that delivers a complete user-facing capability.
- **Decomposition** — Breaking an epic into dependency-ordered, ticket-ready stories.

## Workflow Phases

1. **Discover** — Clarify the problem space, name the user personas, and agree on goals and non-goals.
2. **Specify** — Write the PRD: user stories (INVEST), AC (Given/When/Then), NFRs, edge cases, success metrics.
3. **Validate** — Run `/pm-validate` to get dev feasibility, QA edge cases, and structural gap analysis.
4. **Decompose** — Run `/pm-decompose` to produce dependency-ordered tickets from the validated PRD.
5. **Track** — Run `/pm-report` to pull live status and generate stakeholder updates.

## Key Rules

- **Every user story is INVEST-compliant.** Run `pm-validate` to enforce this before decomposing.
- **Every story has at least one Given/When/Then AC.** Acceptance criteria without this format are not acceptable.
- **Every PRD has an NFR section.** It must cover: performance, security, privacy, accessibility, i18n, and observability.
- **Edge cases are explicitly listed, not implied.** "Happy path only" PRDs are incomplete.
- **Tickets are written from the user perspective.** "As a…" — never "Implement X" or "Add Y to the database."
- **Three Amigos before decompose.** Always run `/pm-validate` before `/pm-decompose`.

## Smallest valuable loop

Draft PRD in `prds/foo.md` → `/pm-validate prds/foo.md` → fix the gaps it flagged → done.
