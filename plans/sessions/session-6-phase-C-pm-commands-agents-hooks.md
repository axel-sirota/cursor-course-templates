# Session 6 — Phase C: PM Commands, Agents, Scripts, Hooks, MCP, Rule

**Phase:** C (PM persona pack)
**Goal:** All functional files for PM persona.
**Depends on:** Session 5 (directory scaffold)
**Next session:** Session 7 (Data Scientist scaffold)

---

## Files to Create

```
personas/pm/
├── commands/
│   ├── pm-validate.md
│   ├── pm-decompose.md
│   └── pm-report.md
├── agents/
│   ├── dev-perspective.md
│   ├── qa-perspective.md
│   └── gap-detector.md
├── scripts/
│   ├── invest-validator.sh
│   ├── ac-format-check.sh
│   └── gap-detector.sh
├── hooks.json
├── mcp.json
└── rules/
    └── 000-pm-workflow.mdc
```

---

## File Specifications

### `commands/pm-validate.md`

**Purpose:** Three Amigos critique on a PRD — dev feasibility + QA edge cases + structural gaps.

Steps:
1. Ask for PRD path (default: latest file in `prds/` or `docs/`)
2. Invoke `dev-perspective` subagent — technical feasibility critique
3. Invoke `qa-perspective` subagent — edge case and testability analysis
4. Invoke `gap-detector` subagent — structural completeness check
5. Synthesize findings into a single validation report at `docs/validation-{prd-name}.md`
6. For each Critical finding, ask PM whether to fix before decomposing

Output: validation report with sections per subagent + a "Ready to decompose?" verdict.

### `commands/pm-decompose.md`

**Purpose:** Break a validated PRD into dependency-ordered tickets for the issue tracker.

Steps:
1. Read PRD + validation report
2. For each user story: create a ticket with title (As a…), description (Given/When/Then AC), size estimate, dependencies
3. Identify dependency order (which tickets block which)
4. Output `docs/tickets-{epic}.md`: ordered list with dependency graph
5. Optional: if Atlassian MCP configured and user confirms, create tickets in Jira

Constraints: tickets from user perspective only; no implementation details; dependency graph must be acyclic.

### `commands/pm-report.md`

**Purpose:** Pull current status from issue tracker and generate a stakeholder status update.

Steps:
1. If Jira MCP available: query active sprint for the epic
2. If GitHub Issues: query open/closed issues with epic label
3. Build status: completed stories / in-progress / blocked (with blocker reason) / not started
4. Generate `docs/status-{date}-{epic}.md`: executive summary + story-by-story status + risks + next milestone

### `agents/dev-perspective.md`

Frontmatter: `name: dev-perspective`, `description: Technical feasibility critique on a PRD`, `model: inherit`, `readonly: true`

For each story asks: feasible as written? what systems are touched that aren't named? race conditions / scaling / consistency concerns? rough cost (S/M/L/unknown)? what pre-existing deps block this?
For each AC: can it be tested by automation? is Given/When/Then specific enough to write a test against?
Output: Feasible as written / Feasible with changes (issue + suggested rewrite) / Hidden complexity / Cost estimate.
Does NOT modify PRD.

### `agents/qa-perspective.md`

Frontmatter: `name: qa-perspective`, `description: Edge case and testability critique`, `model: inherit`, `readonly: true`

For each story lists unnamed edge cases: empty input, max-length input, concurrent access, network failure mid-op, auth missing/expired, permissions insufficient, unexpected state transitions, i18n (non-ASCII, RTL), accessibility (screen reader, keyboard nav).
For each AC: could you write a test for this? are success conditions observable?
Output: Edge cases to add / Untestable criteria / Suggested Given/When/Then rewrites.

### `agents/gap-detector.md`

Frontmatter: `name: gap-detector`, `description: Structural PRD completeness check`, `model: inherit`, `readonly: true`

Checks presence and quality of: goals + non-goals, user personas (named roles), user stories (INVEST), AC (Given/When/Then), NFRs (performance/security/privacy/a11y/i18n/observability), edge cases (explicit), dependencies, rollout plan, success metrics, open questions.
Output: Present (non-empty) / Missing (absent entirely) / Weak (present but underspecified + one-line suggestion).

### `scripts/invest-validator.sh`

Reads `file_path`. Fires only on `*prds/*.md`, `*specs/*.md`, `*docs/prds/*.md`, `*docs/specs/*.md`.
- Scans for lines starting with `As a` / `As an`
- For each such line, checks it contains `I want` and `so that`
- Warns to stderr if not — non-blocking.

### `scripts/ac-format-check.sh`

Reads `file_path`. Same file scope as invest-validator.
- Scans for lines starting with `**Given**`, `**When**`, `**Then**` or `- Given`, `- When`, `- Then`
- If a user story section exists (contains `As a`) but no Given/When/Then follows within 10 lines → warn
- Non-blocking.

### `scripts/gap-detector.sh`

Triggered by `stop`. No file_path.
Prints advisory: "Session ended. Run /pm-validate to check PRD completeness before next session."
Non-blocking.

### `hooks.json`

```json
{
  "version": 1,
  "hooks": {
    "afterFileEdit": [
      { "command": ".cursor/scripts/invest-validator.sh" },
      { "command": ".cursor/scripts/ac-format-check.sh" }
    ],
    "stop": [
      { "command": ".cursor/scripts/gap-detector.sh" }
    ]
  }
}
```

### `mcp.json`

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-atlassian"],
      "env": {
        "JIRA_URL": "${JIRA_URL}",
        "JIRA_USERNAME": "${JIRA_USERNAME}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}",
        "CONFLUENCE_URL": "${CONFLUENCE_URL}",
        "CONFLUENCE_USERNAME": "${CONFLUENCE_USERNAME}",
        "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}"
      },
      "_note": "Override in client-config for internal Jira/Confluence URLs"
    },
    "github-issues": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}" },
      "_note": "Override in client-config for GitHub Enterprise"
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": { "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}" },
      "_note": "Optional. Only configure if your org uses Slack for status updates."
    },
    "notion": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-notion"],
      "env": { "NOTION_API_KEY": "${NOTION_API_KEY}" },
      "_note": "Optional. Only configure if your org uses Notion."
    }
  }
}
```

### `rules/000-pm-workflow.mdc`

Frontmatter: `description: PM persona workflow rules`, `alwaysApply: true`

Sections:
- **INVEST is mandatory** — every story checked before decomposing
- **Given/When/Then required** — every story has at least one AC in this format
- **Three Amigos before decompose** — always run `pm-validate` before `pm-decompose`
- **Subagent delegation:** new story → `dev-perspective`; AC written → `qa-perspective`; PRD complete → `gap-detector`
- **Ticket perspective:** always "As a user…", never "Implement X"

---

## Acceptance Criteria

- [ ] 3 command files, 3 agent files, 3 script files, 1 rule file
- [ ] `hooks.json` and `mcp.json` parse cleanly
- [ ] `mcp.json` has `_note` on atlassian and github-issues
- [ ] `invest-validator.sh` warns on `As a user I do stuff` (missing I want/so that)
- [ ] `invest-validator.sh` passes on `As a user I want to log in so that I can access my dashboard`
- [ ] `ac-format-check.sh` exits 0 on `.py` files (wrong type — no-op)
- [ ] All 3 previous personas still install cleanly
