# Designer Persona

## First 5 minutes

You have three possible starting points. Pick the one that matches what you have right now.

**(a) I have a Figma frame I want in code**
1. Open the Figma desktop app (browser won't work — see Platform gotchas).
2. Select the frame, copy its URL from Figma's share menu.
3. In Claude Code, paste the URL and run:
```
/designer-extract <paste-figma-url>
```
Expect: `docs/figma-context-{frame-name}.md` listing tokens used, components referenced, layout structure, and assets to fetch.

**(b) I have an extracted Figma context, ready to compose**
```
/designer-compose docs/figma-context-{frame}.md
```
Expect: a working prototype using existing codebase components and design tokens — no hardcoded values, no invented variants.

**(c) I have a composed prototype, ready for handoff**
```
/designer-handoff
```
Expect: a PR description + reviewer checklist that makes visual intent legible to engineers.

For mid-prototype refinement, use `/designer-iterate`.

## Platform gotchas

- **Figma DESKTOP app required.** The Dev Mode MCP server runs locally inside the desktop client. The browser version of Figma cannot expose MCP. If `curl http://localhost:3845/health` doesn't respond, the desktop app isn't running or Dev Mode MCP isn't enabled.
- **The roundtrip is one-way for logic.** Claude Code can build a prototype from Figma, and the Figma blog now supports pushing rendered UI back to Figma as editable layers — but the trip loses event handlers, state management, API calls, and business logic. Figma layers carry visual information only.
- **Without Code Connect, AI invents components.** If your codebase has a `<Button>` but Code Connect isn't wired, the AI will generate a new button from scratch and hardcode colors. Run the `token-validator` agent regularly to catch this.
- **Variant tokens leak.** Figma MCP's `get_design_context` sometimes returns base component tokens instead of variant-specific ones. Spot-check colors/spacing in the output before composing.

## What this pack does NOT do

- It does NOT modify business logic. No event handlers, no routes, no API calls, no state management.
- It does NOT invent UI conventions. Every color, spacing, font size, radius, shadow must reference an existing design token.
- It does NOT replace the design review. The `responsive-checker` captures screenshots; humans approve the visual.
- It does NOT push to Figma automatically. You ask for it explicitly ("send this back to Figma").

## What `/architect` produces for this persona

Run `/architect` after `/set-persona designer`. There is no `/setup-stack` for designer (framework-agnostic — adapts to whatever frontend the codebase already uses). Output is NOT a code skeleton — it's a **component plan**:

- `plans/interface-contract.md` — component tree: what exists in the codebase, what needs creating, token requirements, layout structure
- `plans/sessions/session-1-phase-0.md` — Extract session (pull Figma context)
- `plans/sessions/session-N-phase-X.md` — Compose session, Iterate session, Handoff session

No backend, no API design, no routes. Just visual structure.

---

## Mental Model

You ship visual experiences. Your unit of delivery is a prototype that consumes existing design tokens and components, is faithful to the Figma source of truth, and provides a clear engineering handoff. You never invent new UI conventions — you discover what already exists and apply it faithfully.

## Vocabulary

- **Source of truth** — The Figma file. Values come from MCP, not from memory.
- **Design tokens** — Named variables for color, spacing, typography, radius, shadow defined in `tokens.json` / `theme.ts` or equivalent.
- **Components** — Reusable UI building blocks already present in the codebase.
- **Prototype** — A working implementation of a Figma frame using existing tokens and components.
- **Handoff** — A PR description + reviewer checklist that makes visual intent legible to engineers.

## Workflow Phases

1. **Discover** — Understand the Figma frame and the existing codebase component library.
2. **Extract** — Use `/designer-extract` (delegates to `figma-extractor`) to pull tokens, components, and layout from Figma via MCP.
3. **Compose** — Use `/designer-compose` to assemble a working prototype from the extracted context and existing codebase components.
4. **Iterate** — Use `/designer-iterate` to refine the prototype using Visual Editor / Design Mode.
5. **Handoff** — Use `/designer-handoff` to generate a PR description and reviewer checklist.

## Key Rules

- **Keep logic intact.** No modifications to event handlers, routes, API calls, or state management. Logic changes belong to the engineer persona.
- **Minimal diff.** Make the smallest change that achieves the design intent. Do not refactor or reorganize surrounding code.
- **Reuse existing tokens and components.** Never invent new color values, spacing scales, or component variants.
- **Figma is the source of truth.** When in doubt about a value, fetch it via MCP — do not guess from memory or visual inspection.
- **No hardcoded values.** Every color, spacing, font size, line height, border radius, and shadow must reference a design token.

## Active Tools

This persona requires the Figma MCP server (see `SETUP.md`), Playwright MCP for screenshot capture, and Context7 MCP for framework-specific token conventions.

Run `/designer-extract` to begin after completing `SETUP.md`.

## Smallest valuable loop

Select Figma frame → paste URL → `/designer-extract` → read `docs/figma-context-{frame}.md` → done.
