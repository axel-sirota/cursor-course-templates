# Component Spec: StatusBadge

> Northwind Expenses (fictional). Copy to `workspaces/designer/plans/components/status-badge.md` if you want to annotate it.

## Job
A small pill that shows either a claim's status or one policy flag. It appears in every ExpenseRow, in the claim header and in the My Claims filters.

## Status
to build: `src/components/StatusBadge.tsx`

## Props
| Prop | Type | Required | Example | Notes |
|---|---|---|---|---|
| status | `'draft' \| 'submitted' \| 'approved' \| 'rejected' \| 'paid'` | one of status / flag | `'approved'` | status variant. Maps to `data-status` |
| flag | `'RECEIPT_REQUIRED' \| 'OVER_MEAL_LIMIT' \| 'WEEKEND_REVIEW' \| 'ALCOHOL'` | one of status / flag | `'ALCOHOL'` | flag variant. Maps to `data-flag` |

Pass exactly one of `status` or `flag`. Type it as a union so TypeScript rejects both or neither:

```ts
export type ClaimStatus = 'draft' | 'submitted' | 'approved' | 'rejected' | 'paid';
export type PolicyFlag = 'RECEIPT_REQUIRED' | 'OVER_MEAL_LIMIT' | 'WEEKEND_REVIEW' | 'ALCOHOL';
export type StatusBadgeProps =
  | { status: ClaimStatus; flag?: never }
  | { flag: PolicyFlag; status?: never };
```

## Copy (fixed, not passed in)
| Value | Visible text |
|---|---|
| draft | Draft |
| submitted | Submitted |
| approved | Approved |
| rejected | Rejected |
| paid | Paid |
| RECEIPT_REQUIRED | Receipt required |
| OVER_MEAL_LIMIT | Over meal limit |
| WEEKEND_REVIEW | Weekend review |
| ALCOHOL | Alcohol |

The word is always visible. Color is never the only signal.

## Anatomy
```
status variant                     flag variant
┌ span.status-badge ─┐             ┌ span.status-badge ───────────┐
│  Approved          │             │ [!] Receipt required         │
└────────────────────┘             └──────────────────────────────┘
data-variant="status"              data-variant="flag"
data-status="approved"             data-flag="RECEIPT_REQUIRED"
                                   [!] = inline svg, aria-hidden="true"
```

The flag variant has a leading warning icon so flags and statuses differ by shape as well as color.

## Variants and states
| Variant | Trigger | Visual change | Token |
|---|---|---|---|
| draft | `status='draft'` | text + fill | `color.status.draft.text`, `color.status.draft.bg` |
| submitted | `status='submitted'` | text + fill | `color.status.submitted.text`, `color.status.submitted.bg` |
| approved | `status='approved'` | text + fill | `color.status.approved.text`, `color.status.approved.bg` |
| rejected | `status='rejected'` | text + fill | `color.status.rejected.text`, `color.status.rejected.bg` |
| paid | `status='paid'` | text + fill | `color.status.paid.text`, `color.status.paid.bg` |
| flag (all four) | `flag=...` | amber text + fill + icon | `color.flag.text`, `color.flag.bg` |

Not interactive. No hover, focus or disabled state.

## Tokens
| Part | Property | Semantic token |
|---|---|---|
| Badge | padding block | `space.inset.xs` |
| Badge | padding inline | `space.inline.sm` |
| Badge | gap (icon to text) | `space.inline.xs` |
| Badge | radius | `radius.badge` |
| Badge | font size | `font.size.caption` |
| Badge | font weight | `font.weight.semibold` |
| Badge | line height | `font.lineHeight.tight` |
| Icon | width and height | MISSING: propose `size.icon.sm` (12px). Add it to `tokens/tokens.json` first |

## Accessibility
- Renders a `<span>`. No role needed: the visible text is the accessible name.
- The flag icon is decorative: `aria-hidden="true"` and `focusable="false"`.
- Contrast pairs: each `color.status.*.text` on its `.bg`, and `color.flag.text` on `color.flag.bg`. Already covered by exercise 1's `pairs.json`.

## Tests required (`StatusBadge.test.tsx`)
Test titles must contain these phrases (the check matches them, case does not matter):

- [ ] `renders the label for each status`
- [ ] `maps status to data-status`
- [ ] `renders policy flags with text`
- [ ] `has no axe violations`

## Stories required (`StatusBadge.stories.tsx`)
`Draft`, `Submitted`, `Approved`, `Rejected`, `Paid`, `FlagReceiptRequired`, `FlagOverMealLimit`, `FlagWeekendReview`, `FlagAlcohol`
