# Session 5 — Phase C: PM Persona Scaffold

**Phase:** C (PM persona pack)
**Goal:** Directory skeleton + persona.md + README + SETUP + .env.example for pm.
**Depends on:** Session 1 complete (directory layout pattern established)
**Parallel with:** Sessions 3–4 (Designer), 7–8 (DS), 9 (DS stack)
**Next session:** Session 6 (PM commands + agents + hooks)

---

## Files to Create

```
personas/pm/
├── persona.md
├── README.md
├── SETUP.md
├── .env.example
├── commands/
├── agents/
├── scripts/
└── rules/
```

---

## File Specifications

### `personas/pm/persona.md`

- **Mental model:** Ship clarity. Unit of delivery = PRD that engineering can build, with INVEST stories, Given/When/Then AC, edge cases identified, tickets decomposed and dependency-ordered.
- **Vocabulary:** PRD / User story (INVEST) / Acceptance criteria (Given/When/Then) / Three Amigos / Epic / Decomposition
- **Workflow phases:** Discover → Specify → Validate → Decompose → Track
- **Key rules:**
  - Every user story is INVEST-compliant — run `pm-validate` to enforce
  - Every story has at least one Given/When/Then AC
  - Every PRD has a section for NFRs (performance, security, accessibility)
  - Edge cases are explicitly listed, not implied
  - Tickets are written from user perspective ("As a…"), not engineer perspective ("Implement…")

### `personas/pm/README.md`

- **Commands:** `pm-validate`, `pm-decompose`, `pm-report`
- **Subagents:** `dev-perspective`, `qa-perspective`, `gap-detector`
- **Hooks:** `afterFileEdit` (markdown in `prds/`/`docs/`) → invest-validator + ac-format-check; `stop` → gap-detector
- **MCPs:** Atlassian (Jira + Confluence), GitHub Issues, Slack (optional), Notion (optional)
- **Why no `setup-stack`:** PM work produces markdown artifacts + external service operations — not tied to a tech stack
- **Prerequisites:** see SETUP.md

### `personas/pm/SETUP.md`

1. AI code assistant
2. Atlassian credentials: generate API token at id.atlassian.com, set `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`, `CONFLUENCE_URL`
3. Optional: Slack bot token, Notion API key
4. Repository access + smoke test: `/set-persona`, pick `pm`, test Atlassian MCP by listing Jira projects

### `personas/pm/.env.example`

```
# PM Persona — Environment Variables

# Required for Atlassian MCP (Jira + Confluence)
JIRA_URL=https://yourcompany.atlassian.net
# _note: Your instructor provides the org-specific URL
JIRA_USERNAME=you@example.com
JIRA_API_TOKEN=
# _note: Generate at https://id.atlassian.com/manage-profile/security/api-tokens
CONFLUENCE_URL=https://yourcompany.atlassian.net/wiki
# _note: Usually JIRA_URL + /wiki — your instructor confirms
CONFLUENCE_USERNAME=you@example.com
CONFLUENCE_API_TOKEN=
# _note: Same token as JIRA_API_TOKEN works for both

# Required for GitHub Issues MCP
GITHUB_PAT=ghp_your_token_here
# _note: Override in client-config for GitHub Enterprise

# Optional: Slack
SLACK_BOT_TOKEN=
# _note: Provided by your instructor if org uses Slack integration

# Optional: Notion
NOTION_API_KEY=
# _note: Provided by your instructor if org uses Notion
```

---

## Acceptance Criteria

- [ ] `ls personas/pm/` shows correct structure
- [ ] `persona.md` explicitly states INVEST and Given/When/Then requirements
- [ ] `SETUP.md` has Atlassian credential setup with token generation URL
- [ ] `.env.example` has `_note` on every field that a client would override
- [ ] Designer and engineer persona directories unchanged
