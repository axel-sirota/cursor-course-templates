# Phase Checklist

Check every box before moving to the next phase.

---

## Phase 0: Skeleton
- [ ] `tokens/tokens.json` has `primitive` and `semantic` layers
- [ ] `npm run check:tokens` passes
- [ ] `npm run build:tokens` writes `src/styles/tokens.css`
- [ ] Every component in the inventory has a `.tsx`, `.css`, `.test.tsx` and `.stories.tsx`
- [ ] Placeholders render and `npm test` passes
- [ ] `plans/interface-contract.md` lists token set, component inventory (exists / to build) and screen layout

---

## Phase 1: Tokens
- [ ] Every value named in the screen specs maps to a semantic token
- [ ] No semantic token holds a raw value (all are references)
- [ ] Text / surface pairs meet contrast: 4.5:1 body text, 3:1 large text and UI parts
- [ ] Token changes listed in the transition doc with a reason

---

## Phase 2: Components
- [ ] Each component matches its component spec (props, variants, states)
- [ ] Component CSS uses `var(--*)` only, no `--primitive-*`
- [ ] No `style={{ }}` anywhere
- [ ] No fetch, store, effect or formatting logic in components
- [ ] Render test, state test and axe test per component, all green
- [ ] One story per state

---

## Phase 3: Screens
- [ ] Screen file only arranges components, no new colors or spacing
- [ ] Layout matches the screen spec at mobile, tablet and desktop widths
- [ ] Empty, loading and error states from the spec are present as stories
- [ ] `responsive-checker` run if a layout changed

---

## Phase 4: Handoff
- [ ] `npm run check:tokens && npm test && npm run typecheck` all pass
- [ ] `token-validator` agent run on every touched component, zero violations
- [ ] `/designer-handoff` output lists components changed, tokens added, `// TODO: engineering` stubs
- [ ] Open style questions written in `plans/transitions/latest.md`
