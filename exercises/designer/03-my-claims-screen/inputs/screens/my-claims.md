# Screen Spec: My Claims

> Northwind Expenses (fictional). Copy to `workspaces/designer/screens/my-claims.md` before running `/designer-extract`.

## Purpose
An employee opens My Claims to see where each claim stands, find expenses with policy flags, and pick draft expenses to submit.

## Breakpoints
| Name | Viewport | Token | Claim summary grid | Expenses table |
|---|---|---|---|---|
| Mobile | 360 (smallest supported) | MISSING: `breakpoint.sm` = 360px | 1 column | scrolls sideways inside its own region, page does not |
| Tablet | 768 | MISSING: `breakpoint.md` = 768px | 2 columns | full table, scrolls sideways if needed |
| Desktop | 1280 | MISSING: `breakpoint.lg` = 1280px | 4 columns | full table, no sideways scroll |

Page content stops growing at MISSING `size.page.max` (1200px) and centers.

**Media query gotcha.** CSS variables do not work inside `@media (min-width: ...)`. Media queries are the one place a px literal is allowed in component CSS, and it must equal a `breakpoint.*` token with a comment naming it:

```css
@media (min-width: 768px) { /* breakpoint.md */ ... }
```

The responsive-checker agent defaults to 375 / 768 / 1440. Ask it for this spec's widths: 360 / 768 / 1280.

## Layout
```
┌────────────────────────────────────────────────────────────┐
│ PageHeader                                                 │
│  h1 "My claims"            [ New claim ] (primary button)  │
│  "October 2026 · 20 expenses"  (muted)                     │
├────────────────────────────────────────────────────────────┤  gap: space.stack.lg
│ h2 "Claims"                                                │
│ ┌ClaimSummaryCard┐┌ClaimSummaryCard┐┌──────┐┌──────┐        │  grid gap: space.stack.md
│ └────────────────┘└────────────────┘└──────┘└──────┘        │  columns: 1 / 2 / 4
├────────────────────────────────────────────────────────────┤  gap: space.stack.lg
│ h2 "Expenses"                                              │
│ FilterBar                                                  │
│  [All] [Draft] [Submitted] [Approved] [Rejected] [Paid]    │  toggle buttons, gap: space.inline.xs
│  [x] Flagged only     Search merchant [__________]         │
├────────────────────────────────────────────────────────────┤  gap: space.stack.md
│ BulkBar (only when 1+ rows selected)                       │
│  "2 selected"                  [ Submit selected ]         │
├────────────────────────────────────────────────────────────┤
│ ExpensesTable  (region, scrolls sideways on mobile)        │
│  caption "Expenses, October 2026"                          │
│  thead: [select all] Merchant Date Category Amount Status  │
│         Flags Receipt                                      │
│  tbody: ExpenseRow × n                                     │
└────────────────────────────────────────────────────────────┘
page background: color.surface.page, page padding: space.inset.md (mobile), space.inset.lg (tablet and up)
```

## Components
| Region | Component | Status | Props / notes |
|---|---|---|---|
| Header | PageHeader | to build (can live inside the screen file) | title, subtitle, action label |
| Claim summaries | ClaimSummaryCard | **exists but flawed**: `inputs/flawed/ClaimSummaryCard.tsx` + `.css`. Fix it before use | see the fixed props in `assets/sample-claims.json` → `claims` |
| Filters | FilterBar | to build (can live inside the screen file) | status toggles use `aria-pressed`, search input has a visible label |
| Bulk actions | BulkBar | to build (can live inside the screen file) | count text + primary button |
| Table | ExpensesTable | to build | `<table>` with `<caption>`, `<th scope="col">`, ExpenseRow × n |
| Row | ExpenseRow | exists (exercise 2) | |
| Badge, amount | StatusBadge, AmountCell | exist (exercise 2) | used through ExpenseRow and ClaimSummaryCard |

Build the screen in `src/screens/MyClaimsScreen.tsx`. It only arranges components and passes props. No fetching, no filtering logic, no sorting.

Suggested screen props:

```ts
type MyClaimsScreenProps = {
  state: 'ready' | 'loading' | 'empty' | 'error' | 'no-results';
  claims: ClaimSummary[];            // from sample-claims.json → claims
  rows: ExpenseRowData[];            // from sample-claims.json → rows
  selectedIds: string[];
  activeStatus: 'all' | ClaimStatus;
  flaggedOnly: boolean;
};
```

## Tokens used
| Role | Semantic token |
|---|---|
| Page background | `color.surface.page` |
| Page padding | `space.inset.md` → `space.inset.lg` from `breakpoint.md` |
| Region gap | `space.stack.lg` |
| Grid and table gap | `space.stack.md` |
| Page title | `font.size.page`, `font.weight.bold` |
| Section heading (h2) | `font.size.heading`, `font.weight.semibold` |
| Subtitle, caption | `color.text.muted`, `font.size.label` |
| Primary buttons | `color.action.primary.bg`, `color.action.primary.bgHover`, `color.text.inverse`, `radius.control` |
| Toggle button, pressed | `color.action.primary.bg` fill, `color.text.inverse` text |
| Toggle button, not pressed | `color.surface.card` fill, `color.border.control` border, `color.text.default` text |
| Focus ring (all controls) | `color.focus.ring`, `border.width.focus` |
| Table container | `color.surface.card`, `radius.card`, `color.border.subtle` |
| Table header text | `font.size.caption`, `font.weight.semibold`, `color.text.muted` |
| Breakpoints | MISSING: `breakpoint.sm`, `breakpoint.md`, `breakpoint.lg` |
| Max content width | MISSING: `size.page.max` (1200px) |
| Min claim card width | MISSING: `size.card.min` (280px). Grid: `repeat(auto-fill, minmax(var(--size-card-min), 1fr))` |
| Loading placeholder fill | MISSING: `color.surface.skeleton` (gray 200) |
| Error banner fill | MISSING: `color.feedback.danger.bg` (red 100) |
| Error banner border | MISSING: `color.feedback.danger.border` (red 700) |

Every MISSING token goes into `tokens/tokens.json` before the screen uses it, with a reason in the transition doc. Then prove the new pairs:

```bash
node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs \
  --pairs exercises/designer/03-my-claims-screen/checks/pairs-screen.json
```

## States
| State | `state` prop | What shows | Story name |
|---|---|---|---|
| Default | `ready` | 8 claim cards, filters, 20 rows | `Default` |
| Loading | `loading` | 4 card-shaped and 5 row-shaped placeholders, region has `aria-busy="true"`, visually hidden text "Loading claims" | `Loading` |
| Empty | `empty` | "No expenses yet" + "New claim" button. No table, no filters | `Empty` |
| Error | `error` | Banner with `role="alert"`: "We could not load your claims." + "Try again" button. Uses `color.feedback.danger.*` and `color.text.danger` | `Error` |
| Filtered, no results | `no-results` | Filters stay visible, table replaced by "No expenses match these filters" + "Clear filters" text button | `FilteredNoResults` |
| Mobile | `ready` at 360 | one column of cards, table scrolls inside its region | `Mobile` |
| Tablet | `ready` at 768 | two columns of cards | `Tablet` |
| Desktop | `ready` at 1280 | four columns of cards | `Desktop` |

For the viewport stories, add custom 360 / 768 / 1280 viewports to `.storybook/preview.ts` and set each story's viewport parameter (see the Storybook viewport docs for your version).

## Accessibility
- One `h1` ("My claims"), then `h2` for "Claims" and "Expenses". Claim cards use `h3`.
- The table region on mobile: `role="region"`, `aria-labelledby` pointing at the caption, `tabIndex={0}` so keyboard users can scroll it.
- Status toggles are `<button type="button" aria-pressed>`. Not color only: the pressed button also gets a check icon or bold text.
- Select-all checkbox is labelled "Select all expenses".
- Error banner uses `role="alert"`. The loading region uses `aria-busy`.

## Sample content
Use `exercises/designer/assets/sample-claims.json`: `rows` (20 expense lines) and `claims` (8 summaries). The `Default` story uses all of them. Paid rows have `disabled: true`.

## Interactions (stubs only)
| Element | Event | Engineering note |
|---|---|---|
| New claim | click | `// TODO: engineering` open the new claim form |
| Status toggle | click | `// TODO: engineering` update the status filter |
| Flagged only | change | `// TODO: engineering` update the flag filter |
| Search | input | `// TODO: engineering` filter by merchant |
| Select all, row checkbox | change | `// TODO: engineering` update selection |
| Submit selected | click | `// TODO: engineering` submit selected draft expenses |
| ClaimSummaryCard view details / more actions | click | `// TODO: engineering` |
| Try again | click | `// TODO: engineering` refetch |
| Clear filters | click | `// TODO: engineering` reset filters |

## Open questions
- Should Submit selected skip rows that are not drafts, or should non-draft rows be disabled too? Today only paid rows are disabled. Raise it in the handoff.
- Do breakpoints belong in `tokens/tokens.json` if CSS cannot read them in media queries? Proposed: yes, as the single source for Storybook viewports, docs and any future build step.
