# PM Persona

All PM work lives in `workspaces/pm/`. Paths in this pack are relative to that folder.

## First 5 minutes

```
/set-persona add pm
/setup-stack pm              # pm-prd-markdown
/architect pm                # PRD outline in plans/, then prds/<name>.md with every section headed
/start-session pm
```

Then pick the starting point that matches what you have right now.

**(a) I have raw notes / a meeting transcript / a stakeholder ask**
Paste the notes into Cursor chat. Ask: "Draft a PRD scaffold from these notes in `prds/draft-{name}.md`. Include goals, non-goals, INVEST user stories, Given/When/Then AC, NFRs, edge cases." Iterate in markdown until the draft holds water.

**(b) I have a draft PRD in `prds/`**
```
/pm-validate prds/my-feature.md
```
Expect: `docs/validation-my-feature.md` with a Three Amigos critique (dev feasibility, QA edge cases, structural gap analysis). Resolve flagged items, re-run if needed.

**(c) I have a validated PRD ready for engineering**
```
/pm-decompose prds/my-feature.md
```
Expect: dependency-ordered tickets in `docs/tickets-{epic}.md`. That file is the deliverable. Pushing to Jira is optional, only if you configured an Atlassian MCP yourself.

`/pm-report` reads the `Status` field of each ticket in that file and writes a status snapshot. End every session with `/next-session`.

## Platform gotchas

- **PRDs live in `prds/*.md`, one story per file in `stories/*.md` (the PRD only holds an index table linking to them). Jira / Confluence are optional push targets, not your editor.** You will spend most of your time in markdown files in the workspace.
- **Rules and hooks only see the workspace.** `.cursor/rules/pm/` and the INVEST / AC hooks fire for files under `workspaces/pm/`. A PRD saved at the repo root gets no checks.
- **The AI doesn't know your product unless you tell it.** Put a 5-line product summary (target users, what the product does, key constraints) at the top of `plans/interface-contract.md`; `/start-session pm` loads it. Generic PRDs come from generic context. Use synthetic product details only.
- **No issue tracker MCP ships with this pack.** Tickets and status live in markdown. If you add an Atlassian MCP on your own, smoke-test it ("list my Jira projects") before relying on it.

## What this pack does NOT do

- It does NOT write code for you. Use the engineer persona for that.
- It does NOT decide product strategy. It enforces structure on decisions you make.
- It does NOT replace stakeholder conversations. It captures their outcomes.
- It does NOT auto-push to Jira. You review tickets in markdown first, then push.

## What `/architect pm` produces

Run `/architect pm` after `/setup-stack pm`. Output is **structured documentation**, not code:

- `plans/interface-contract.md`: PRD outline (problem, goals, non-goals, users, epics, NFR categories, success metrics)
- `plans/sessions/session-1-phase-0.md`: skeleton session, which scaffolds `prds/<name>.md` (every required heading, TODO bodies), `stories/` (one story per file) and `glossary.md`
- `plans/sessions/session-N-phase-X.md`: Specify, Validate, Decompose sessions

The "skeleton" is the PRD document tree.

---

## Mental Model

You ship clarity. Your unit of delivery is a PRD that engineering can build without guessing: INVEST-compliant user stories, Given/When/Then acceptance criteria, explicit edge cases, and tickets decomposed and dependency-ordered so the sprint starts with confidence.

## Vocabulary

- **PRD**: Product Requirements Document, the authoritative description of what to build and why.
- **User story (INVEST)**: a story that is Independent, Negotiable, Valuable, Estimable, Small, and Testable.
- **Acceptance criteria (Given/When/Then)**: machine-verifiable conditions that define "done" for each story.
- **Three Amigos**: a collaborative review with dev, QA, and PM perspectives before work begins.
- **Epic**: a collection of related stories that delivers a complete user-facing capability.
- **Decomposition**: breaking an epic into dependency-ordered, ticket-ready stories.

## Workflow Phases

1. **Discover**: clarify the problem space, name the user personas, and agree on goals and non-goals.
2. **Specify**: write the PRD: user stories (INVEST), AC (Given/When/Then), NFRs, edge cases, success metrics.
3. **Validate**: run `/pm-validate` to get dev feasibility, QA edge cases, and structural gap analysis.
4. **Decompose**: run `/pm-decompose` to produce dependency-ordered tickets from the validated PRD.
5. **Track**: update ticket status in `docs/tickets-{epic}.md`, then run `/pm-report` to generate stakeholder updates.

## Key Rules

- **Every user story is INVEST-compliant.** Run `/pm-validate` to enforce this before decomposing.
- **Every story has at least one Given/When/Then AC.** Acceptance criteria without this format are not acceptable.
- **Every PRD has an NFR section.** It must cover: performance, security, privacy, accessibility, i18n, and observability.
- **Edge cases are explicitly listed, not implied.** "Happy path only" PRDs are incomplete.
- **Tickets are written from the user perspective.** "As a…", never "Implement X" or "Add Y to the database."
- **Three Amigos before decompose.** Always run `/pm-validate` before `/pm-decompose`.

## Smallest valuable loop

Draft PRD in `prds/foo.md` → `/pm-validate prds/foo.md` → fix the gaps it flagged → `/next-session`.
