# Screen Spec: {Screen Name}

> Save as `screens/{screen-name}.md`. This file replaces a Figma frame when none exists.

## Purpose
One sentence. Who looks at this screen and what they decide here.

## Breakpoints
| Name | Min width token | Columns |
|---|---|---|
| Mobile | (default) | 1 |
| Tablet | `breakpoint.md` | 2 |
| Desktop | `breakpoint.lg` | 3 |

## Layout
Top to bottom. Name the region, the component, and the spacing token between regions.

```
┌──────────────────────────────┐
│ Header            (PageHeader)│
├──────────────────────────────┤  gap: space.stack.lg
│ Card grid   (BudgetCard × n) │  gap: space.stack.md
├──────────────────────────────┤
│ Footer action     (Button)   │
└──────────────────────────────┘
```

## Components
| Region | Component | Status | Props from spec |
|---|---|---|---|
| Header | PageHeader | exists / to build | title, subtitle |
| Card grid | BudgetCard | exists / to build | label, spentLabel, limitLabel, percentUsed, status |

## Tokens used
| Role | Semantic token |
|---|---|
| Page background | `color.surface.page` |
| Region gap | `space.stack.lg` |

If a role has no token, write `MISSING` and propose a name. Do not pick a raw value.

## States
| State | What shows | Story name |
|---|---|---|
| Default | data present | `Default` |
| Empty | no items, message + action | `Empty` |
| Loading | placeholder blocks | `Loading` |
| Error | message + retry | `Error` |

## Sample content
Fictional data only. List the exact strings the stories and tests use.

## Interactions (stubs only)
| Element | Event | Engineering note |
|---|---|---|
| Card | click | `// TODO: engineering` open category detail |

## Open questions
- 
