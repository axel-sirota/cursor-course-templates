# Designer Persona Pack

This pack adds designer-specific commands, subagents, hooks, MCP integrations, and rules to the Adaptive SDLC. It is installed by running `/set-persona designer`.

## What this pack adds

**Commands:**
- `/designer-extract` — Pull design tokens, components, and layout from a Figma file via MCP; saves context to `docs/figma-context-{frame-name}.md`
- `/designer-compose` — Assemble a working prototype from Figma context using existing codebase components and tokens
- `/designer-iterate` — Refine the composed prototype using Visual Editor / Design Mode in an interactive loop
- `/designer-handoff` — Generate a PR description and reviewer checklist for visual changes

**Subagents:**
- `figma-extractor` — Read-only Figma context fetcher via MCP; extracts tokens, components, layout, and assets
- `token-validator` — Scans styling files for hardcoded values and suggests matching design tokens
- `responsive-checker` — Verifies visual changes across mobile, tablet, and desktop breakpoints via Playwright

**Hooks:**
- `afterFileEdit` — Runs `token-validator.sh` (CSS/SCSS/TSX/JSX/Vue/Svelte) and `no-inline-styles.sh` (TSX/JSX) on every changed file; advisory only
- `stop` — Runs `screenshot-compare.sh` to remind you to capture breakpoint screenshots at session end

**MCP servers:**
- `figma` — Figma Dev Mode MCP (requires Figma desktop app running + `FIGMA_ACCESS_TOKEN`)
- `playwright` — Browser automation for screenshot capture and responsive verification
- `context7` — Up-to-date library documentation for framework-specific token conventions (Tailwind, MUI, Chakra, etc.)

## Why no `setup-stack`

The designer persona is framework-agnostic. It works with any frontend framework — React, Vue, Svelte, or plain CSS. The codebase already has its framework; this persona adapts to it rather than prescribing one. Stack-specific token conventions are resolved at runtime via Context7 MCP.

## How this pack composes with the engineer pack

The designer persona operates on the visual layer only. After handoff, the engineer persona takes the PR description and implements any remaining logic stubs. The two personas share no hooks and do not conflict.

## Prerequisites

See `SETUP.md` for the full pre-class checklist, including Figma desktop app setup and Dev Mode MCP configuration.
