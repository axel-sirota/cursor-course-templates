# Designer Persona Pack

Turns design tokens and markdown screen specs into reusable React components in `workspaces/designer/`, with no hardcoded values and Figma as an optional extra.

Install with `/set-persona add designer`, then `/setup-stack designer` (designer-react-tokens) → `/architect designer` → `/start-session designer`. All paths below are relative to `workspaces/designer/`.

## What this pack adds

**Commands:**
- `/designer-extract`: pull tokens, components and layout from a screen spec plus `tokens/tokens.json` (default) or a Figma frame (optional); saves `docs/design-context-{screen}.md` or `docs/figma-context-{frame}.md`
- `/designer-compose`: assemble a working prototype from that context using existing components and tokens
- `/designer-iterate`: refine the composed prototype in Cursor's browser panel in an interactive loop
- `/designer-handoff`: generate `docs/PR_DESCRIPTION.md` and a reviewer checklist for visual changes

**Subagents:**
- `token-validator`: scans styling files for hardcoded values and suggests matching design tokens
- `responsive-checker`: verifies visual changes across mobile, tablet, and desktop breakpoints via Playwright
- `figma-extractor`: read-only Figma context fetcher via MCP (optional Figma path only)

**Hooks** (installed to `.cursor/scripts/designer/`, scoped to `workspaces/designer/`):
- `afterFileEdit`: `token-validator.sh` (CSS/SCSS/TSX/JSX/Vue/Svelte) and `no-inline-styles.sh` (TSX/JSX) on every changed file; advisory only
- `stop`: `screenshot-compare.sh` reminds you to capture breakpoint screenshots at session end

**MCP servers** (no tokens needed):
- `playwright`: browser automation for screenshot capture and responsive verification
- `context7`: up-to-date library documentation for framework-specific token conventions

`figma` is not installed by default. `SETUP.md` → "Optional: Figma" shows the block to add by hand (needs `FIGMA_ACCESS_TOKEN`).

## How this pack pairs with `/setup-stack`

The designer stack is `designer-react-tokens`. It sets the Architecture Shape to "Design System" (token JSON with primitive and semantic layers, React components, Storybook stories) and installs its rules into `.cursor/rules/designer/` next to this pack's rules. Both apply only to files in `workspaces/designer/`.

## How this pack composes with the engineer pack

The designer persona operates on the visual layer only. After handoff, the engineer persona takes the PR description and implements any remaining logic stubs. The two personas work in separate workspaces and share no hooks.

## Prerequisites

See `SETUP.md` for the pre-class checklist. Figma setup there is optional.
