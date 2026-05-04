# Session 4 — Phase B: Designer Commands, Agents, Scripts, Hooks, MCP, Rule

**Phase:** B (Designer persona pack)
**Goal:** All functional files for designer persona.
**Depends on:** Session 3 (directory scaffold)
**Parallel with:** Sessions 2, 6, 8 — each persona's commands session is independent
**Next session:** Session 10 (set-persona command, needs all persona packs complete)

---

## Files to Create

```
personas/designer/
├── commands/
│   ├── designer-extract.md
│   ├── designer-compose.md
│   ├── designer-iterate.md
│   └── designer-handoff.md
├── agents/
│   ├── figma-extractor.md
│   ├── token-validator.md
│   └── responsive-checker.md
├── scripts/
│   ├── token-validator.sh
│   ├── no-inline-styles.sh
│   └── screenshot-compare.sh
├── hooks.json
├── mcp.json
└── rules/
    └── 000-designer-workflow.mdc
```

---

## File Specifications

### `commands/designer-extract.md`

**Purpose:** Pull design tokens, components, and layout from a Figma file via MCP.

Steps:
1. Ask for Figma URL or frame node ID
2. Delegate to `figma-extractor` subagent
3. Subagent saves to `docs/figma-context-{frame-name}.md`
4. Report path + summary (token count, component count, asset count)

Output: markdown file with token table, component variant matrix, layout description, asset URLs. Consumed by `designer-compose`.

### `commands/designer-compose.md`

**Purpose:** Assemble working prototype from Figma context + existing codebase components.

Steps:
1. Read `docs/figma-context-{frame-name}.md`
2. For each component in layout: search codebase for existing match → use it; if not found, ask whether to create or reuse similar
3. Apply layout using existing primitives (flex/grid utilities, spacing tokens)
4. Wire up empty handlers — do NOT invent business logic
5. Output: working component/page + summary of components reused, tokens applied, stubs left for engineering

Constraints enforced by rule: no hardcoded values, no inline styles, no modification of existing handlers.

### `commands/designer-iterate.md`

**Purpose:** Refine composed prototype using Visual Editor / Design Mode.

Steps:
1. Confirm running URL (default: http://localhost:3000)
2. Open Visual Editor / Design Mode in the AI tool
3. Iterate loop: click element → state change in plain language → agent translates to code change → hot reload
4. After 3–5 iterations, suggest invoking `responsive-checker`

This is an interactive loop — no command argument.

### `commands/designer-handoff.md`

**Purpose:** Generate PR description + reviewer checklist for visual changes.

Steps:
1. `git diff main...HEAD --stat` → identify changed files
2. Categorize: visual changes / tokens used / components reused / logic preserved (confirm no handler/route/state files modified)
3. Run `responsive-checker` → capture breakpoint screenshots
4. Generate `PR_DESCRIPTION.md`:
   - What changed (2–4 bullets)
   - What was preserved (explicit list of untouched logic)
   - Screens to review (responsive-checker screenshots)
   - Designer QA checklist (Figma match / breakpoints / tokens)

### `agents/figma-extractor.md`

Frontmatter: `name: figma-extractor`, `description: Read-only Figma context fetcher`, `model: inherit`, `readonly: true`

Steps: Figma MCP fetch → tokens + components + layout + assets → save to `docs/figma-context-{frame}.md` → report path + counts + any inconsistencies (hardcoded values in Figma itself).
Does NOT write component implementation.

### `agents/token-validator.md`

Frontmatter: `name: token-validator`, `description: Scans styling files for hardcoded values`, `model: inherit`, `readonly: true`

Scans for: hex colors, `rgb()`/`rgba()`/`hsl()`, named colors, pixel values in margin/padding/gap/width/height (except 0 and 1px borders), hardcoded font-size/weight/line-height, hardcoded border-radius.
For each violation: look up matching token in `tokens.json`/`theme.ts`/tokens file.
Output: Violation (file+line+value+suggested token) / Unmatched (no obvious token → flag for human).
Uses Context7 MCP for framework-specific token conventions (Tailwind, MUI, Chakra).

### `agents/responsive-checker.md`

Frontmatter: `name: responsive-checker`, `description: Verifies visual changes across breakpoints`, `model: inherit`, `readonly: false`

Steps: identify running URL → Playwright MCP screenshots at 375×667 (mobile), 768×1024 (tablet), 1440×900 (desktop) → save to `docs/responsive/{breakpoint}-{page}.png` → note overflow/broken layout/hidden content/truncation → report pass/fail per breakpoint + suggested fixes referencing existing responsive utilities.

### `scripts/token-validator.sh`

Reads `file_path` from stdin JSON. Fires on `.css/.scss/.tsx/.jsx/.vue/.svelte` only.
- grep for `#[0-9a-fA-F]{3,6}` outside comments → warn
- grep for `(margin|padding|gap):\s*[0-9]+px` excluding `0px`/`1px` → warn
Non-blocking (warns to stderr, exits 0).

### `scripts/no-inline-styles.sh`

Reads `file_path`. Fires on `.tsx/.jsx` only.
- grep for `style=\{\{` → warn "Use className with design tokens"
Non-blocking.

### `scripts/screenshot-compare.sh`

Triggered by `stop`. No file_path needed.
Creates `docs/screenshots/` if missing.
Prints advisory: "Session ended. Run /responsive-checker to generate breakpoint screenshots."
Non-blocking.

### `hooks.json`

```json
{
  "version": 1,
  "hooks": {
    "afterFileEdit": [
      { "command": ".cursor/scripts/token-validator.sh" },
      { "command": ".cursor/scripts/no-inline-styles.sh" }
    ],
    "stop": [
      { "command": ".cursor/scripts/screenshot-compare.sh" }
    ]
  }
}
```

### `mcp.json`

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp", "--figma-api-key=${FIGMA_ACCESS_TOKEN}", "--stdio"],
      "env": {},
      "_note": "Requires Figma desktop app running with Dev Mode MCP enabled. Override in client-config for org-level access."
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"],
      "env": {}
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {}
    }
  }
}
```

### `rules/000-designer-workflow.mdc`

Frontmatter: `description: Designer persona workflow rules`, `alwaysApply: true`

Three guardrails (always enforced):
1. Keep logic intact — no handlers/routes/state
2. Minimal diff — smallest change achieving intent
3. Reuse tokens and components

Figma is source of truth — when in doubt, check via MCP.

Subagent delegation:
- Style file edited → `token-validator`
- Layout change complete → `responsive-checker`
- Figma URL provided → `figma-extractor`

---

## Acceptance Criteria

- [ ] `ls personas/designer/commands/` → 4 files
- [ ] `ls personas/designer/agents/` → 3 files
- [ ] `ls personas/designer/scripts/` → 3 files
- [ ] `hooks.json` and `mcp.json` parse cleanly
- [ ] `mcp.json` has `_note` on figma server
- [ ] `token-validator.sh` exits 0 on a `.py` file (wrong file type — should no-op)
- [ ] `no-inline-styles.sh` exits 0 on a `.css` file (wrong file type — should no-op)
- [ ] Run `/set-persona engineer` after building designer — confirm engineer installs cleanly (no designer files bleed over)
