# Exercise 2: Claim Components

**Time:** 90 to 120 minutes
**Needs:** Exercise 1 done (a passing `workspaces/designer/tokens/tokens.json`)
**You produce:** `StatusBadge`, `AmountCell` and `ExpenseRow` in `workspaces/designer/src/components/`, each with `.tsx`, `.css`, `.test.tsx` and `.stories.tsx`, built from semantic tokens only.

## Scenario

Engineering is about to build the My Claims screen. They asked design for three parts they can drop in: a status pill, a money cell that lines up in a column, and the expense row that holds both. They want every state in Storybook so QA can review without running the app, and they want proof the parts pass an accessibility scan.

## Inputs

| File | What it is |
|---|---|
| `inputs/component-specs/StatusBadge.md` | 5 statuses + policy flag variant, copy, tokens, required tests and stories |
| `inputs/component-specs/AmountCell.md` | currency code, refunds, right alignment, tabular numbers |
| `inputs/component-specs/ExpenseRow.md` | row anatomy, hover / focus / selected / disabled, MISSING tokens to add |
| `../assets/sample-claims.json` | 20 fictional rows. Field names match `ExpenseRow` props |
| `checks/required.json` | the stories and test titles the check requires |
| `checks/pairs-rows.json` | extra contrast pairs for the row hover and selected fills |

## Task

0. **Copy the sample data** so stories and tests can import it without long relative paths:
   `mkdir -p workspaces/designer/src/data && cp exercises/designer/assets/sample-claims.json workspaces/designer/src/data/`
   JSON imports widen `"USD"` to `string`, so cast the union fields once in a small `src/data/sample.ts` helper.
1. **Add the MISSING tokens first.** The specs name `size.icon.sm`, `color.surface.hover`, `color.surface.selected` and `color.border.selected`. Add primitives if needed, then the semantic tokens, then prove contrast with `pairs-rows.json`. Write the reason for each new token in the transition doc.
2. **Build StatusBadge, then AmountCell, then ExpenseRow.** ExpenseRow must import the other two, not copy their markup.
3. **Tokens only.** No hex, `rgb()`, named colors, px / rem font sizes, or spacing literals in component CSS (`1px` borders and `0` are fine). No `--primitive-*` variables. No `style={{ }}`.
4. **One story per state** listed in each spec, with the exact export names. ExpenseRow stories wrap the row in `<table><tbody>` with a decorator.
5. **Tests:** render tests and an axe scan per component. Disable axe's `color-contrast` rule in jsdom (it cannot compute color) and rely on `check_contrast.mjs` for contrast, as the stack example does.
6. **No logic.** Props arrive display-ready. `onOpen` and `onSelectedChange` default to empty stubs marked `// TODO: engineering`.

Look at `workspaces/designer/examples/budget-card/` for the file layout, test style and CSS guard tests.

## Commands to use

```
/architect designer exercises/designer/02-claim-components/README.md
/start-session designer
/designer-extract exercises/designer/02-claim-components/inputs/component-specs/StatusBadge.md
/designer-compose docs/design-context-status-badge.md
/designer-iterate                 # Storybook on http://localhost:6006
...repeat extract / compose / iterate for AmountCell and ExpenseRow...
/designer-handoff
/next-session
```

- Run the `token-validator` agent on each component before you call it done.
- In `/designer-iterate`, review each story at 360px wide in the Storybook viewport toolbar. ExpenseRow will be wide. Exercise 3 handles the narrow layout, so note what breaks rather than fixing it here.
- If the agent wants to invent a token, stop it and add the token to `tokens/tokens.json` yourself (spec change first).

## How it is checked

Run from the repo root:

```bash
# 1. Required files, stories and test titles
node exercises/designer/02-claim-components/checks/check_stories.mjs
#    Other workspace: --root path/to/workspace

# 2. Contrast for the new row fills (exercise 1's checker, this exercise's pairs)
node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs \
  --pairs exercises/designer/02-claim-components/checks/pairs-rows.json

# 3. Tests, types and token schema
cd workspaces/designer && npm test && npm run typecheck && npm run check:tokens && cd ../..

# 4. Quick hardcoded-value sweep (should print nothing)
grep -rnE '#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(|style=\{\{|--primitive-' workspaces/designer/src/components
```

`check_stories.mjs` has no dependencies. It looks for `X.tsx`, `X.css`, `X.stories.tsx` and `X.test.tsx`, a default export in the stories file, every required story export (commented-out stories do not count), and an `it()` / `test()` title containing each required phrase. It prints a table and exits 1 if anything is missing. A passing run ends with:

```
[stories] OK: 53 check(s) present
```

## Done when

- [ ] `check_stories.mjs` exits 0 (53 checks)
- [ ] `check_contrast.mjs --pairs .../pairs-rows.json` exits 0 (10 pairs)
- [ ] `npm test` passes, including an axe scan with zero violations per component
- [ ] `npm run typecheck` passes. Passing both `status` and `flag` to StatusBadge is a type error
- [ ] The grep sweep prints nothing
- [ ] Status, refund, receipt and selection all read without color (word, sign, icon shape, checkbox)
- [ ] Disabled rows use `color.text.muted`, not `opacity`
- [ ] Every new token is in `tokens/tokens.json` with a reason in the transition doc

## Stretch

- **Pseudo-states.** Add the Storybook pseudo-states addon that matches your Storybook major version and make the `Hover` story show the hover fill without a pointer.
- **Real data stories.** Import `sample-claims.json` in a story and render all 20 rows in one `AllRows` story. Do the amounts line up?
- **Interaction test.** Give `Selected` a `play` function that clicks the checkbox and asserts the stub was called, using `fn()` from `@storybook/test`.
- **Optional Figma path.** If you have a Figma component set for the badge, run `/designer-extract <figma-frame-url>` and diff its values against your tokens.
