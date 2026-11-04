# Brand Brief: Northwind Expenses

> Northwind Co. is a fictional company made up for this course. All names, colors and numbers are invented.

## Who this is for

Northwind Expenses is the internal app Northwind staff use to file expense claims, attach receipts and track reimbursement. Finance reviewers use the same app to approve or reject claims. People open it on a laptop at their desk and on a phone at the airport, so it must read well at 360px wide.

## Brand colors

Two brand colors. Both are fixed by the brand team.

| Name | Hex | Brand team note |
|---|---|---|
| Northwind Navy | `#1B3A5C` | Headers, primary text accents, the logo |
| Harbor Teal | `#0F8B8D` | Accent color. Marketing would like primary buttons in Harbor Teal |

Approved tints and shades. You may use these, and only these, as primitive values.

| Family | 100 | 300 | 500 | 700 | 900 |
|---|---|---|---|---|---|
| navy | `#E3ECF5` | | `#2F5F8F` | `#1B3A5C` | `#0E2236` |
| teal | `#DFF3F3` | `#5CC5C7` | `#0F8B8D` | `#0A6466` | |

## Neutrals

| Name | Hex |
|---|---|
| white | `#FFFFFF` |
| gray 100 | `#F5F7FA` |
| gray 200 | `#E4E7EB` |
| gray 400 | `#9AA5B1` |
| gray 500 | `#7B8794` |
| gray 600 | `#52606D` |
| gray 700 | `#3E4C59` |
| gray 900 | `#1F2933` |

The app background is gray 100. Cards and tables sit on white.

## Supporting colors (status and feedback)

The app shows five claim statuses and four policy flags. Finance asked for each status to be easy to tell apart at a glance, and never by color alone: every status always shows its word too.

| Family | 100 | 500 | 700 | 800 |
|---|---|---|---|---|
| blue | `#E6EFFF` | `#3D7BE0` | `#1F4FA3` | |
| green | `#E3F5EA` | `#2F9E58` | `#1E6B3A` | |
| red | `#FDE8E8` | `#D64545` | `#A61B1B` | |
| amber | `#FFF4D6` | `#E0A100` | | `#7A4B00` |

Suggested meaning. You decide the exact pairs, as long as they pass the contrast rule below.

| Claim status | Meaning | Suggested family |
|---|---|---|
| draft | Started, not sent | gray |
| submitted | Waiting for a reviewer | blue |
| approved | Reviewer said yes, payment queued | green |
| rejected | Reviewer said no, see comment | red |
| paid | Money sent to the employee | teal (brand) |

| Policy flag | Meaning |
|---|---|
| `RECEIPT_REQUIRED` | Over the receipt threshold and no receipt attached |
| `OVER_MEAL_LIMIT` | Meal above the per-person limit |
| `WEEKEND_REVIEW` | Expense dated on a Saturday or Sunday |
| `ALCOHOL` | Line item includes alcohol |

All four flags share one "needs attention" style (amber is suggested). The flag text tells them apart.

## Typography

Northwind uses the system UI font stack: `system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`.

| Step | Size | Used for |
|---|---|---|
| 100 | 12px | captions, currency codes, flag chips |
| 200 | 14px | table cells, labels |
| 300 | 16px | body text |
| 400 | 20px | card titles |
| 500 | 24px | section headings, large amounts |
| 600 | 32px | page title |

Weights: 400 regular, 600 semibold, 700 bold. Line heights: 1.25 for headings, 1.5 for body.

Amounts are always shown with tabular numbers so columns line up.

## Spacing rhythm

4px base grid. Allowed steps: 4, 8, 12, 16, 24, 32, 48 px.

## Radius

| Use | Value |
|---|---|
| Inputs, buttons, checkboxes | 4px |
| Cards, table container | 8px |
| Badges and chips | 9999px (pill) |

## Borders and focus

- Border width is 1px everywhere. Focus rings are 2px.
- Control borders (inputs, checkboxes) must be visible: at least 3:1 against the surface they sit on.
- Every interactive element shows a visible focus ring. The ring must be at least 3:1 against the surface it sits on.

## The contrast rule (non-negotiable)

Text must pass WCAG 2.2 level AA:

- Normal text: contrast ratio of at least **4.5:1** against its background.
- Non-text parts that carry meaning (focus rings, control borders): at least **3:1**.
- Do not round up. 4.49:1 is a fail.

Some colors in this brief fail when used as text. That is on purpose. The brand team cares more about the rule than about any single color. If a brand color fails for a job, use the nearest approved shade that passes and write down why.

## Token contract (names the checks read)

Build primitive tokens from the colors above, then semantic tokens that name intent. The semantic color tokens below are required with exactly these names, because the automated contrast check looks them up. You may add more.

| Semantic token | Job |
|---|---|
| `color.surface.page` | app background |
| `color.surface.card` | cards, table body |
| `color.text.default` | body text |
| `color.text.muted` | secondary text: dates, categories, captions |
| `color.text.inverse` | text on dark or brand fills |
| `color.text.link` | links and text buttons |
| `color.text.danger` | error messages |
| `color.text.success` | refund amounts, success messages |
| `color.action.primary.bg` | primary button fill |
| `color.action.primary.bgHover` | primary button fill on hover |
| `color.status.{draft,submitted,approved,rejected,paid}.text` | status badge text |
| `color.status.{draft,submitted,approved,rejected,paid}.bg` | status badge fill |
| `color.flag.text` | policy flag chip text |
| `color.flag.bg` | policy flag chip fill |
| `color.border.subtle` | dividers, card outline (decorative) |
| `color.border.control` | input and checkbox borders |
| `color.focus.ring` | focus ring |

Plus semantic tokens for spacing, font size, font weight, line height, radius and border width, following the scales above. Name them by intent (`space.inset.md`, `font.size.body`, `radius.badge`), not by value.
