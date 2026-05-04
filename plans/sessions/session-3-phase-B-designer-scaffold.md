# Session 3 — Phase B: Designer Persona Scaffold

**Phase:** B (Designer persona pack)
**Goal:** Directory skeleton + persona.md + README + SETUP + .env.example for designer.
**Depends on:** Session 2 complete (engineer is the reference — copy structure pattern)
**Next session:** Session 4 (designer commands + agents + hooks)

---

## Files to Create

```
personas/designer/
├── persona.md
├── README.md
├── SETUP.md
├── .env.example
├── commands/          (empty dir)
├── agents/            (empty dir)
├── scripts/           (empty dir)
└── rules/             (empty dir)
```

---

## File Specifications

### `personas/designer/persona.md`

- **Mental model:** Ship visual experiences. Unit of delivery = prototype consuming existing design tokens + components, faithful to Figma source of truth, with a clear engineering handoff.
- **Vocabulary:** Source of truth (Figma) / Design tokens / Components / Prototype / Handoff
- **Workflow phases:** Discover → Extract → Compose → Iterate → Handoff
- **Key rules:**
  - Keep logic intact — no handlers, routes, state management changes
  - Minimal diff — smallest change achieving design intent
  - Reuse existing tokens and components — never invent new conventions
  - Figma is the source of truth — values come from MCP, not from memory
  - No hardcoded values — every color/spacing/font/radius references a token

### `personas/designer/README.md`

- **Commands:** `designer-extract`, `designer-compose`, `designer-iterate`, `designer-handoff`
- **Subagents:** `figma-extractor`, `token-validator`, `responsive-checker`
- **Hooks:** `afterFileEdit` (CSS/SCSS/TSX/JSX) → token-validator + no-inline-styles; `stop` → screenshot-compare
- **MCPs:** Figma (requires desktop app + token), Playwright, Context7
- **Why no `setup-stack`:** designer work is framework-agnostic — the codebase already has its framework
- **Prerequisites:** see SETUP.md

### `personas/designer/SETUP.md`

1. AI code assistant (Cursor or Claude Code)
2. Figma desktop app — enable Dev Mode MCP Server in Preferences
3. Figma access token — generate at figma.com/developers/api#access-tokens
4. Node.js 20+ (for running the prototype)
5. Browser (Chrome/Chromium for Playwright)
6. Repository access + smoke test: `/set-persona`, pick `designer`, confirm Figma MCP listed

### `personas/designer/.env.example`

```
# Designer Persona — Environment Variables

# Required for Figma MCP (Figma desktop app must be running with Dev Mode MCP enabled)
FIGMA_ACCESS_TOKEN=figd_your_token_here
# _note: For org-level Figma access, your instructor provides a shared token

# Optional: Context7 (no auth needed for free tier)
```

---

## Acceptance Criteria

- [ ] `ls personas/designer/` shows same structure as `personas/engineer/` (minus hooks.json and mcp.json — those come in Session 4)
- [ ] `persona.md` explicitly states "Keep logic intact" and "Figma is the source of truth"
- [ ] `SETUP.md` includes Figma desktop app setup with Dev Mode MCP step
- [ ] `.env.example` has `_note` on `FIGMA_ACCESS_TOKEN`
- [ ] Engineer persona directory unchanged
