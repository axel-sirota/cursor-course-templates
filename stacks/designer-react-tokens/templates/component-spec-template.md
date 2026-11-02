# Component Spec: {ComponentName}

> Save next to the screen spec or in `plans/components/{component-name}.md`. Fill it before writing code.

## Job
One sentence. What this component shows and where it appears.

## Status
exists / to build. If it exists, give the file path.

## Props
| Prop | Type | Required | Example | Notes |
|---|---|---|---|---|
| label | `string` | yes | `"Groceries"` | display-ready |
| status | `'on-track' \| 'near-limit' \| 'over'` | yes | `'on-track'` | maps to `data-status` |
| onSelect | `() => void` | no | | stub only, engineering wires it |

Props are display-ready. No raw numbers that need formatting inside the component.

## Anatomy
```
┌ article.component-name ─────────┐
│ h3   title                      │
│ p    supporting text            │
│ progress / meter / button       │
└─────────────────────────────────┘
```

## Variants and states
| Variant | Trigger | Visual change | Token |
|---|---|---|---|
| on-track | `status='on-track'` | status text and bar use success color | `color.status.success` |
| over | `status='over'` | status text and bar use danger color | `color.status.danger` |

## Tokens
| Part | Property | Semantic token |
|---|---|---|
| Container | background | `color.surface.card` |
| Container | padding | `space.inset.md` |
| Title | font size | `font.size.heading` |

## Accessibility
- Element roles and accessible names:
- Contrast pairs to verify (text token on surface token):
- Keyboard behaviour (if interactive):

## Tests required
- [ ] Render with example props, text visible
- [ ] One assertion per variant
- [ ] axe: zero violations

## Stories required
One per row in "Variants and states".
