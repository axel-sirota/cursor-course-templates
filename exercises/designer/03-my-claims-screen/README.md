# Exercise 3: My Claims Screen

**Time:** 90 to 120 minutes
**Needs:** Exercises 1 and 2 done (tokens pass contrast, StatusBadge / AmountCell / ExpenseRow exist)
**You produce:** a fixed `ClaimSummaryCard` and a `MyClaimsScreen` in `workspaces/designer/src/screens/` with every state from the spec, working at 360, 768 and 1280 px.

## Scenario

The My Claims screen is the first page every Northwind employee sees. A contractor built `ClaimSummaryCard` in a hurry for a demo, and engineering wants to reuse it on this screen. Before it goes anywhere, design has to fix it. Then compose the screen from the parts you built in exercise 2, with real loading, empty, error and no-results states.

## Inputs

| File | What it is |
|---|---|
| `inputs/screens/my-claims.md` | screen spec: layout, components, states, breakpoints, MISSING token callouts, stubs |
| `inputs/flawed/ClaimSummaryCard.tsx` | the contractor's component. It has seeded defects. Count them |
| `inputs/flawed/ClaimSummaryCard.css` | its styles. More seeded defects |
| `../assets/sample-claims.json` | `rows` (20 expense lines) and `claims` (8 claim summaries) |
| `checks/required.json` | stories and test titles required for this exercise |
| `checks/pairs-screen.json` | contrast pairs for the error banner, toggles and page text |

## Setup

```bash
mkdir -p workspaces/designer/screens workspaces/designer/src/data
cp exercises/designer/03-my-claims-screen/inputs/screens/my-claims.md workspaces/designer/screens/
cp exercises/designer/03-my-claims-screen/inputs/flawed/ClaimSummaryCard.* workspaces/designer/src/components/
cp exercises/designer/assets/sample-claims.json workspaces/designer/src/data/   # skip if done in exercise 2
```

## Task

### Part A: fix ClaimSummaryCard (30 to 40 minutes)

1. Before touching code, run the defect check on the copy you just made and the `token-validator` agent. Then read the component yourself and write a list of every problem you find, with file and line. Compare your list with the check's list. What did the check miss? What did you miss?
2. Fix every defect with the smallest change. Reuse `StatusBadge` and `AmountCell`. Keep `onOpen` and `onMoreActions` exactly as they are.
3. One fix changes the props contract (the component should not format money). Write it in the handoff as a change engineering must approve. Do not change anything else about how data reaches the card.
4. Add `ClaimSummaryCard.test.tsx` and `ClaimSummaryCard.stories.tsx` with the names in `checks/required.json`.

### Part B: build the screen (60 to 80 minutes)

1. Add every MISSING token from the spec to `tokens/tokens.json` and pass `pairs-screen.json`.
2. Build `src/screens/MyClaimsScreen.tsx` (+ `.css`, `.test.tsx`, `.stories.tsx`). It arranges components and passes props. No fetching, filtering or sorting.
3. Cover every state in the spec's States table, each as a story with the exact name.
4. Add the 360 / 768 / 1280 viewports to `.storybook/preview.ts` and check each in Storybook. The page must never scroll sideways at 360. The table region may.
5. Media queries are the only place px literals are allowed, each with a `/* breakpoint.x */` comment. The `token-validator` hook will warn about them. That warning is expected for media queries only.

## Commands to use

```
/architect designer exercises/designer/03-my-claims-screen/README.md
/start-session designer
/designer-extract screens/my-claims.md
/designer-compose docs/design-context-my-claims.md
/designer-iterate              # Storybook http://localhost:6006, check Mobile / Tablet / Desktop stories
/designer-handoff
/next-session
```

- Ask the `token-validator` agent to scan `src/components/ClaimSummaryCard.*` before and after your fix.
- Ask the `responsive-checker` agent to use **360, 768 and 1280**, not its defaults (375, 768, 1440).
- `/designer-handoff` must list the ClaimSummaryCard props change (`total: number` replaced by a formatted label plus currency) under "needs engineering".

## How it is checked

Run from the repo root:

```bash
# 1. Seeded defect patterns in the fixed card (12 patterns)
node exercises/designer/03-my-claims-screen/checks/check_card.mjs
#    Run it on the original first to see what "broken" looks like:
#    node exercises/designer/03-my-claims-screen/checks/check_card.mjs --dir exercises/designer/03-my-claims-screen/inputs/flawed

# 2. Stories and test titles for the card and the screen
node exercises/designer/02-claim-components/checks/check_stories.mjs \
  --required exercises/designer/03-my-claims-screen/checks/required.json

# 3. Contrast for the new state tokens
node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs \
  --pairs exercises/designer/03-my-claims-screen/checks/pairs-screen.json

# 4. Everything still passes
node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs
node exercises/designer/02-claim-components/checks/check_stories.mjs
cd workspaces/designer && npm test && npm run typecheck && npm run check:tokens && cd ../..

# 5. Sweep (should print nothing)
grep -rnE '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(|style=\{\{|--primitive-' \
  workspaces/designer/src/components workspaces/designer/src/screens
```

`check_card.mjs` looks for patterns, so a pass means none of the known mistakes are left. It does not prove the card is good. Storybook, axe and your own review do that.

## Done when

- [ ] `check_card.mjs` prints `OK: none of the 12 defect patterns found`
- [ ] `check_stories.mjs --required .../03-my-claims-screen/checks/required.json` exits 0
- [ ] `check_contrast.mjs` passes with the default pairs, `pairs-rows.json` and `pairs-screen.json`
- [ ] `npm test` and `npm run typecheck` pass, axe finds zero violations in every screen state
- [ ] At 360 px: one column of cards, no sideways page scroll, table scrolls inside its region and the region takes keyboard focus
- [ ] At 768 px: two columns. At 1280 px: four columns, content stops at `size.page.max`
- [ ] Every MISSING token from the spec is in `tokens/tokens.json` with a reason in the transition doc
- [ ] Every interactive element has an empty handler marked `// TODO: engineering`
- [ ] Your own defect list is in the transition doc, with what the automated check missed

## Stretch

- **Stacked rows on mobile.** Instead of sideways scroll, turn each row into a stacked card below `breakpoint.md`. If you change `display` on table elements, add explicit `role="table"`, `row`, `cell` and `columnheader`, because some browsers drop table semantics when `display` changes. Re-run axe.
- **Token-driven media queries.** Extend a copy of `build-tokens.mjs` to also write `src/styles/breakpoints.css` with `@custom-media` rules from `breakpoint.*`. What extra build step does that need before browsers understand it?
- **Optional Figma path.** If your team has a My Claims frame, run `/designer-extract <figma-frame-url>` and compare the result with `docs/design-context-my-claims.md`. Which values disagree with the spec?
