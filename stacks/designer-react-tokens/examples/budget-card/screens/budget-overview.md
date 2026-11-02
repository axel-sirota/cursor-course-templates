# Screen Spec: Budget Overview

> Fictional app "Pocketplan". All names and amounts are made up for the course.

## Purpose
A user opens this screen at any point in the month to see which spending categories are on track and which need attention.

## Breakpoints
| Name | Min width | Columns |
|---|---|---|
| Mobile | default | 1 |
| Tablet | 768 (proposed token `breakpoint.md`, MISSING) | 2 |
| Desktop | 1200 (proposed token `breakpoint.lg`, MISSING) | 3 |

Breakpoint tokens are not in `tokens/tokens.json` yet. Propose them before building the screen grid.

## Layout
```
┌──────────────────────────────────────────────┐
│ PageHeader: "March budget" / "12 days left"  │
├──────────────────────────────────────────────┤  gap: space.stack.lg
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│ │ BudgetCard │ │ BudgetCard │ │ BudgetCard │ │  gap: space.stack.md
│ └────────────┘ └────────────┘ └────────────┘ │
│ ┌────────────┐                               │
│ │ BudgetCard │                               │
│ └────────────┘                               │
├──────────────────────────────────────────────┤  gap: space.stack.lg
│ Button: "Add category"                       │
└──────────────────────────────────────────────┘
page background: color.surface.page, page padding: space.inset.md
```

## Components
| Region | Component | Status | Props |
|---|---|---|---|
| Header | PageHeader | to build | title, subtitle |
| Card grid | BudgetCard | exists (`src/components/BudgetCard.tsx`) | label, spentLabel, limitLabel, percentUsed, status, statusLabel |
| Footer | Button | to build | label, onClick (stub) |

## Tokens used
| Role | Semantic token |
|---|---|
| Page background | `color.surface.page` |
| Page padding | `space.inset.md` |
| Gap between regions | `space.stack.lg` |
| Gap between cards | `space.stack.md` |
| Header title size | `font.size.heading` |
| Header subtitle color | `color.text.muted` |
| Grid breakpoints | MISSING: `breakpoint.md`, `breakpoint.lg` |

## Status rules (decided by the parent, not the card)
| Share of limit used | status | statusLabel pattern |
|---|---|---|
| under 85% | `on-track` | "$X left" |
| 85% to 100% | `near-limit` | "$X left" |
| over 100% | `over` | "$X over" (percentUsed clamped to 100) |

## States
| State | What shows | Story name |
|---|---|---|
| Default | four cards below | `BudgetOverview/Default` |
| Empty | "No categories yet" + Add category button | `BudgetOverview/Empty` |
| Loading | four card-shaped placeholders | `BudgetOverview/Loading` |

## Sample content
| label | spentLabel | limitLabel | percentUsed | status | statusLabel |
|---|---|---|---|---|---|
| Groceries | $420 | $600 | 70 | on-track | $180 left |
| Dining out | $185 | $200 | 93 | near-limit | $15 left |
| Transport | $162 | $150 | 100 | over | $12 over |
| Utilities | $95 | $240 | 40 | on-track | $145 left |

## Interactions (stubs only)
| Element | Event | Engineering note |
|---|---|---|
| BudgetCard | click | `// TODO: engineering` open category detail |
| Add category | click | `// TODO: engineering` open create-category form |

## Open questions
- Should the over-budget card also show an icon, or is color plus text enough? Text is already present, so color is not the only signal.
- Do breakpoints belong in the token file or in a layout config? Proposed: token file, `$type: dimension`.
