# Designer Exercises: Northwind Expenses

Three exercises that take a designer from a brand brief to a working, accessible screen in Cursor. The product is **Northwind Expenses**, the internal expense app of the fictional Northwind Co. Staff file claims, attach receipts and track reimbursement.

No Figma account is needed. Every input is a markdown brief, a markdown spec or a JSON file. A Figma path is listed as a stretch in each exercise for teams that have one.

## Domain in one table

| Concept | Values |
|---|---|
| Claim status | `draft`, `submitted`, `approved`, `rejected`, `paid` |
| Policy flag | `RECEIPT_REQUIRED`, `OVER_MEAL_LIMIT`, `WEEKEND_REVIEW`, `ALCOHOL` |
| Currency | `USD`, `EUR`, `GBP`, `CAD` (always shown as a code: USD and CAD both use `$`) |
| Sample data | `assets/sample-claims.json`: 20 expense rows, 8 claim summaries |

## The exercises

| # | Exercise | Time | You build | Checked by |
|---|---|---|---|---|
| 1 | [Brand to Tokens](01-brand-to-tokens/README.md) | 60 to 75 min | `tokens/tokens.json`: primitive + semantic layers, every text pair WCAG AA | `checks/check_contrast.mjs` (18 pairs) + `build-tokens.mjs --check` |
| 2 | [Claim Components](02-claim-components/README.md) | 90 to 120 min | `StatusBadge`, `AmountCell`, `ExpenseRow`, one story per state, render + axe tests | `checks/check_stories.mjs` (53 checks) + contrast for row fills + `npm test` |
| 3 | [My Claims Screen](03-my-claims-screen/README.md) | 90 to 120 min | fix a flawed `ClaimSummaryCard` (12 seeded defects), compose `MyClaimsScreen` with all states at 360 / 768 / 1280 | `checks/check_card.mjs` (12 patterns) + `check_stories.mjs --required` (34 checks) + contrast for state tokens + `npm test` |

Total: about 4 to 5 hours. Each exercise builds on the previous one in the same workspace.

## Flow

```
/set-persona add designer
/setup-stack designer                                              # designer-react-tokens
/architect designer exercises/designer/01-brand-to-tokens/README.md   # README is the plan source
/start-session designer
  /designer-extract  → docs/design-context-*.md
  /designer-compose  → components and screens from tokens only
  /designer-iterate  → Storybook (http://localhost:6006) or Vite (http://localhost:5173)
  /designer-handoff  → docs/PR_DESCRIPTION.md
/next-session                                                      # transition doc: decisions, new tokens
```

Run `/architect designer exercises/designer/<exercise>/README.md` at the start of each exercise so the plan in `workspaces/designer/plans/` follows that exercise.

All work lives in `workspaces/designer/`. The persona's rules and hooks only fire there.

## Checks

Every check is a plain Node 20+ script with no dependencies. Run them from the repo root. Each prints a table and exits 1 when something fails, so they work in CI too.

| Script | What it proves | Default input |
|---|---|---|
| `01-brand-to-tokens/checks/check_contrast.mjs` | WCAG 2.x contrast for declared fg / bg token pairs, resolving semantic references | `workspaces/designer/tokens/tokens.json`, `--pairs` to swap the pair list |
| `02-claim-components/checks/check_stories.mjs` | co-located files, story exports, test titles | `workspaces/designer`, `--required` to swap the list |
| `03-my-claims-screen/checks/check_card.mjs` | none of the 12 seeded defect patterns remain | `workspaces/designer/src/components` |

Pair lists reused across exercises: `01-.../checks/pairs.json` (base), `02-.../checks/pairs-rows.json` (row hover and selected), `03-.../checks/pairs-screen.json` (error banner, toggles).

What the scripts cannot see: whether a story shows the right state, how the screen looks at each width, and whether the copy makes sense. Storybook, the `responsive-checker` agent and a human review cover that. axe runs inside the Vitest tests with the `color-contrast` rule off, because jsdom cannot compute colors. Contrast is proven on the token pairs instead.

## For instructors

Each exercise has a `SOLUTION.md` with the traps, expected decisions, grading notes and reference code. The reference code was run end to end (Vitest + axe, `tsc`, all three checks) in a scratch copy of the stack example. Do not hand `SOLUTION.md` to students before they finish.
