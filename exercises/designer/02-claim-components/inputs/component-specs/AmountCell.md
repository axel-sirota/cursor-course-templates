# Component Spec: AmountCell

> Northwind Expenses (fictional).

## Job
Shows one money amount with its currency code, right-aligned with tabular numbers so a column of amounts lines up. Used in ExpenseRow and in claim totals.

## Status
to build: `src/components/AmountCell.tsx`

## Props
| Prop | Type | Required | Example | Notes |
|---|---|---|---|---|
| amountLabel | `string` | yes | `"$1,234.50"`, `"−$45.00"` | formatted by the parent, sign included. The component never formats numbers |
| currency | `'USD' \| 'EUR' \| 'GBP' \| 'CAD'` | yes | `'CAD'` | always shown as a code |
| kind | `'charge' \| 'refund'` | no, default `'charge'` | `'refund'` | maps to `data-kind` |

Why the code is always visible: USD and CAD both use `$`. "$120.00" alone does not tell a reviewer which one it is.

## Anatomy
```
┌ span.amount-cell ─────────────────────────┐
│                     $1,234.50  USD        │   charge
│               −$45.00  USD  Refund        │   refund
└───────────────────────────────────────────┘
  span.amount-cell__value     (tabular numbers)
  span.amount-cell__currency  (caption, muted)
  span.amount-cell__kind      ("Refund", only when kind="refund")
```

The component renders inline content. Put it inside a `<td>` (ExpenseRow does) or any block. The outer span is block-level and end-aligned (for example `display: flex; justify-content: flex-end`) so it fills the cell and hugs the right edge.

## Variants and states
| Variant | Trigger | Visual change | Token |
|---|---|---|---|
| charge | `kind='charge'` or omitted | default text color | `color.text.default` |
| refund | `kind='refund'` | value in success color, visible word "Refund" | `color.text.success` |
| per currency | `currency=...` | code text only, no color change | `color.text.muted` |

Refund is never color only: the minus sign comes in `amountLabel` and the word "Refund" is visible.

## Tokens
| Part | Property | Semantic token |
|---|---|---|
| Value | font size | `font.size.label` (in rows) |
| Value | font weight | `font.weight.semibold` |
| Value | color | `color.text.default` / `color.text.success` |
| Currency, Refund | font size | `font.size.caption` |
| Currency, Refund | color | `color.text.muted` |
| Gap between parts | column gap | `space.inline.xs` |

Not a token, required anyway: `font-variant-numeric: tabular-nums` on the value. This is a keyword, not a hardcoded value, so it is allowed.

## Accessibility
- Plain text. Screen readers read "minus 45 dollars USD Refund" or similar, depending on the minus character. The visible word "Refund" makes the meaning clear either way.
- Contrast: `color.text.success` and `color.text.muted` on `color.surface.card` (exercise 1 pairs 4 and 9).

## Tests required (`AmountCell.test.tsx`)
- [ ] `renders the amount and currency code`
- [ ] `marks refunds with text`
- [ ] `uses tabular numbers` (read `AmountCell.css` and assert `tabular-nums` is there)
- [ ] `has no axe violations`

## Stories required (`AmountCell.stories.tsx`)
`Usd`, `Eur`, `Gbp`, `Cad`, `Refund`, `LargeAmount`

Sample args: Usd `$86.40`, Eur `€1,150.00`, Gbp `£42.75`, Cad `$310.20`, Refund `−$45.00 USD`, LargeAmount `$12,480.00 USD`. Pull more from `exercises/designer/assets/sample-claims.json`.
