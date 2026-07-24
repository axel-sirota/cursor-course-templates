---
description: Implement one feature spec across all three services with parallel subagents, then merge in dependency order
---

# Implement Across Services Command

## Usage
`/implement-across-services <spec-file>`

If no spec file is given, default to `specs/feature-refunds.md`.

## Execution

**1. Read the spec**
- Read `<spec-file>` IN FULL before spawning anything. Identify the slice that
  belongs to each service (Gateway / Payments / Notifications sections and
  their acceptance criteria).
- Implement only what is NOT yet implemented: sections marked "your turn"
  (e.g. Part 1.5) are the work; sections marked "teams lab only" (Part 2) are
  out of scope for this command. If everything is already implemented, report
  that instead of spawning agents.

**2. Spawn the implementers**

Spawn ALL THREE implementer agents SIMULTANEOUSLY:

1. **gateway-implementer** — the Gateway slice of the spec
2. **payments-implementer** — the Payments slice of the spec
3. **notifications-implementer** — the Notifications slice of the spec

**CRITICAL**: Run these in PARALLEL using multiple Agent tool calls in a
single message, not sequentially.

Each agent gets ONLY its service's slice of the spec plus the shared
`contracts/` schemas — not the whole feature.

> **Note — where the branches come from**: each subagent works in an isolated
> worktree; its branch appears as `worktree-<name>` under `.claude/worktrees/`.
> The setting `worktree.baseRef: "head"` in `.claude/settings.json` makes those
> worktrees branch from YOUR current HEAD, not from `main` — that is why the
> setting exists. Do not remove it.

**3. Wait for completion reports**
- Wait for all three agents to return their JSON completion reports. Do not
  start merging while any agent is still running.

**4. MERGE PHASE (you are the sole merger)**
- Merge each agent's worktree branch back **sequentially**, in dependency
  order:
  1. `payments`
  2. `notifications`
  3. `gateway`
- After EACH merge, run `contracts/validate.sh <service-dir>` for the service
  just merged (e.g. `bash contracts/validate.sh services/payments`).
- **Stop on the first failure** and fix it before continuing to the next
  merge. Never merge on top of a failing validation.

**5. Unified report**

Emit one table, one row per service:

| Service | Branch | Status | Files changed | Validate result |
|---------|--------|--------|---------------|-----------------|
| payments | worktree-... | merged / failed | ... | pass / fail |
| notifications | worktree-... | merged / failed | ... | pass / fail |
| gateway | worktree-... | merged / failed | ... | pass / fail |

Then list the combined next steps — run the three test suites:

```bash
npm test --workspace services/payments
npm test --workspace services/notifications
npm test --workspace services/gateway
```
