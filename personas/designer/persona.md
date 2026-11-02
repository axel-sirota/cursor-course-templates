# Designer Persona

All designer work lives in `workspaces/designer/`. Paths in this pack are relative to that folder.

## First 5 minutes

```
/set-persona add designer
/setup-stack designer        # designer-react-tokens
/architect designer          # token set + component inventory in plans/, then tokens/, components, stories
/start-session designer
```

Then pick the starting point that matches what you have right now. No Figma account is needed.

**(a) I have a screen spec and a token file (default)**
```
/designer-extract screens/{screen-name}.md
```
Expect: `docs/design-context-{screen-name}.md` listing the semantic tokens the screen needs from `tokens/tokens.json`, the components it names, the layout structure, and any value that has no token yet.

**(b) I have an extracted context, ready to compose**
```
/designer-compose docs/design-context-{screen-name}.md
```
Expect: a working component or screen built from existing components and design tokens. No hardcoded values, no invented variants.

**(c) I have a composed prototype, ready for handoff**
```
/designer-handoff
```
Expect: `docs/PR_DESCRIPTION.md` plus a reviewer checklist that makes visual intent legible to engineers.

For mid-prototype refinement, use `/designer-iterate`. End every session with `/next-session`.

**Optional: I have a Figma frame.** After adding the optional Figma MCP server (see `SETUP.md`), run `/designer-extract <figma-frame-url>`. Output goes to `docs/figma-context-{frame-name}.md` and feeds `/designer-compose` the same way.

## Platform gotchas

- **Tokens first, components second.** A value that is not in `tokens/tokens.json` gets added there first, with a reason in the transition doc. Never invent it inside a component.
- **`src/styles/tokens.css` is generated.** Rebuild it from the token JSON (`npm run build:tokens`); do not edit it by hand.
- **Rules and hooks only see the workspace.** `.cursor/rules/designer/` and the token hooks fire for files under `workspaces/designer/`.
- **Figma is optional and not installed by default.** Add the `figma` MCP server by hand (see `SETUP.md`). It can return base component values instead of variant ones; spot-check against `tokens/tokens.json` before composing.
- **Local URLs:** the Vite dev server runs on `http://localhost:5173`, Storybook on `http://localhost:6006`.

## What this pack does NOT do

- It does NOT modify business logic. No event handlers, no routes, no API calls, no state management.
- It does NOT invent UI conventions. Every color, spacing, font size, radius, shadow must reference a design token.
- It does NOT replace the design review. The `responsive-checker` captures screenshots; humans approve the visual.
- It does NOT need Figma, and it does NOT push to Figma.

## What `/architect designer` produces

Run `/architect designer` after `/setup-stack designer`. Output is a **component plan**, then a token-driven skeleton:

- `plans/interface-contract.md`: token set (semantic over primitive), component inventory (exists / to build), screen layout
- `plans/sessions/session-1-phase-0.md`: skeleton session (`tokens/tokens.json`, placeholder components, one story per component)
- `plans/sessions/session-N-phase-X.md`: Extract, Compose, Iterate, Handoff sessions

No backend, no API design, no routes. Just visual structure.

---

## Mental Model

You ship visual experiences. Your unit of delivery is a prototype that consumes existing design tokens and components, is faithful to the screen spec, and comes with a clear engineering handoff. You never invent new UI conventions. You discover what already exists and apply it faithfully.

## Vocabulary

- **Source of truth**: `tokens/tokens.json` plus the markdown screen specs in `screens/`. A Figma file, when used, feeds the same token names.
- **Design tokens**: named variables for color, spacing, typography, radius, shadow. Primitive tokens hold raw values; semantic tokens name intent and reference primitives.
- **Components**: reusable UI building blocks in `src/components/`.
- **Prototype**: a working screen built from existing tokens and components.
- **Handoff**: a PR description + reviewer checklist that makes visual intent legible to engineers.

## Workflow Phases

1. **Discover**: read the screen spec and the existing component library.
2. **Extract**: `/designer-extract` pulls tokens, components and layout from the spec (or from Figma via `figma-extractor`).
3. **Compose**: `/designer-compose` assembles a working prototype from the extracted context and existing components.
4. **Iterate**: `/designer-iterate` refines the prototype in Cursor's browser panel.
5. **Handoff**: `/designer-handoff` generates a PR description and reviewer checklist.

## Key Rules

- **Keep logic intact.** No modifications to event handlers, routes, API calls, or state management. Logic changes belong to the engineer persona.
- **Minimal diff.** Make the smallest change that achieves the design intent.
- **Reuse existing tokens and components.** Never invent new color values, spacing scales, or component variants.
- **The token file is the source of truth.** When in doubt about a value, read it from `tokens/tokens.json`. Do not guess from memory or visual inspection.
- **No hardcoded values.** Every color, spacing, font size, line height, border radius, and shadow must reference a design token.

## Smallest valuable loop

Pick a screen spec → `/designer-extract screens/{screen}.md` → read `docs/design-context-{screen}.md` → `/next-session`.
