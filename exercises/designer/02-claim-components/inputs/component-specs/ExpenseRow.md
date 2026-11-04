# Component Spec: ExpenseRow

> Northwind Expenses (fictional).

## Job
One expense line in the My Claims table: who was paid, when, what for, how much, where the claim stands, which policy flags fired, and whether a receipt is attached. People scan dozens of these, select some, and open one.

## Status
to build: `src/components/ExpenseRow.tsx`. Reuses `StatusBadge` and `AmountCell`. Do not copy their markup.

## Props
| Prop | Type | Required | Example | Notes |
|---|---|---|---|---|
| merchant | `string` | yes | `"Harbor Grill"` | |
| dateLabel | `string` | yes | `"Fri 16 Oct 2026"` | formatted by the parent |
| dateTime | `string` | yes | `"2026-10-16"` | ISO date for `<time dateTime>` |
| category | `string` | yes | `"Meals"` | |
| amountLabel | `string` | yes | `"$86.40"` | passed to AmountCell |
| currency | `'USD' \| 'EUR' \| 'GBP' \| 'CAD'` | yes | `'USD'` | passed to AmountCell |
| kind | `'charge' \| 'refund'` | no | `'charge'` | passed to AmountCell |
| status | `ClaimStatus` | yes | `'submitted'` | passed to StatusBadge |
| flags | `PolicyFlag[]` | yes | `['OVER_MEAL_LIMIT']` | empty array for none |
| hasReceipt | `boolean` | yes | `true` | |
| selected | `boolean` | no, default `false` | | checkbox checked, `data-selected` |
| disabled | `boolean` | no, default `false` | | row cannot be selected (paid claims), `data-disabled` |
| onSelectedChange | `(selected: boolean) => void` | no | | stub only: `// TODO: engineering` |
| onOpen | `() => void` | no | | stub only: `// TODO: engineering` |

Field names match `exercises/designer/assets/sample-claims.json`, so a story can spread a sample row straight into the props.

## Anatomy
```
tr.expense-row  [data-selected] [data-disabled]
├ td  input[type=checkbox]   aria-label="Select Harbor Grill, Fri 16 Oct 2026"
├ td  button.expense-row__open  "Harbor Grill"        (text button, opens the claim)
├ td  time[dateTime]  "Fri 16 Oct 2026"               (muted)
├ td  "Meals"                                         (muted)
├ td  AmountCell                                      (right-aligned)
├ td  StatusBadge status
├ td  ul[aria-label="Policy flags"] > li > StatusBadge flag   (cell empty when no flags)
└ td  receipt icon (svg, aria-hidden) + visually hidden text "Receipt attached" / "No receipt"
```

The row renders a `<tr>`. Stories and tests wrap it in `<table><tbody>...</tbody></table>` (a Storybook decorator and a small test helper).

Receipt icon: two different shapes (paperclip / paperclip with a slash), not one icon in two colors.

## Variants and states
| State | Trigger | Visual change | Token |
|---|---|---|---|
| default | none | white row, subtle bottom border | `color.surface.card`, `color.border.subtle` |
| hover | pointer over row (`:hover`) | row fill changes | MISSING: propose `color.surface.hover` (gray 100) |
| focus | keyboard focus on checkbox or merchant button (`:focus-visible`) | 2px ring on the focused control, row keeps hover fill via `:focus-within` | `color.focus.ring`, `border.width.focus` |
| selected | `selected` | checkbox checked, row fill changes, 2px leading accent bar | MISSING: propose `color.surface.selected` (navy 100) and `color.border.selected` (navy 700) |
| disabled | `disabled` | checkbox disabled, merchant still opens the claim, text switches to muted | `color.text.muted` (never `opacity`) |
| with flags | `flags.length > 0` | one flag badge per flag | via StatusBadge |
| missing receipt | `hasReceipt=false` | "no receipt" icon and hidden text | `color.text.danger` on the icon is fine, the text carries the meaning |
| refund | `kind='refund'` | via AmountCell | via AmountCell |

Disabled must stay readable. Fading the row with `opacity` drops muted text below 4.5:1. Use the muted text token instead.

The new surface tokens need contrast proof. Add them to `tokens/tokens.json`, then run exercise 1's checker with this exercise's extra pairs:

```bash
node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs \
  --pairs exercises/designer/02-claim-components/checks/pairs-rows.json
```

## Tokens
| Part | Property | Semantic token |
|---|---|---|
| Row | background | `color.surface.card` |
| Row | bottom border | `border.width.default` solid `color.border.subtle` |
| Cell | padding | `space.inset.sm` block, `space.inline.md` inline |
| Cell text | font size | `font.size.label` |
| Merchant | font weight | `font.weight.semibold` |
| Merchant button | color | `color.text.link` |
| Date, category | color | `color.text.muted` |
| Checkbox | border | `color.border.control` |
| Focus ring | outline | `border.width.focus` solid `color.focus.ring` |
| Flags list | gap | `space.inline.xs` |
| Receipt icon | size | `size.icon.sm` (from the StatusBadge spec) |

## Accessibility
- Checkbox accessible name includes merchant and date so 20 checkboxes are not all "Select".
- Merchant is a real `<button type="button">`, not a clickable `<td>`.
- Receipt state is text for screen readers, icon for sight. Not color.
- Every interactive element has a visible `:focus-visible` style. Do not remove the outline without replacing it.
- Contrast pairs: text default, text muted, link and focus ring on `color.surface.hover` and `color.surface.selected` (`checks/pairs-rows.json`).

## Tests required (`ExpenseRow.test.tsx`)
- [ ] `renders merchant, date, category and amount`
- [ ] `renders the status badge`
- [ ] `renders each policy flag`
- [ ] `announces receipt status`
- [ ] `selected row checks the checkbox`
- [ ] `disabled row disables the checkbox`
- [ ] `has no axe violations`

## Stories required (`ExpenseRow.stories.tsx`)
`Default`, `Hover`, `Focused`, `Selected`, `Disabled`, `WithPolicyFlags`, `MissingReceipt`, `Refund`

- `Focused`: use a `play` function that focuses the checkbox (`@storybook/test` is already in the stack).
- `Hover`: CSS `:hover` cannot be triggered from a script. Either add the Storybook pseudo-states addon that matches your Storybook major version, or keep the story and write in its `parameters.docs.description.story` how to check hover by hand. Both are accepted.
