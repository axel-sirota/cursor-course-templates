# Vibe: Design System Architecture

## The shape
```
tokens.json ──build──▶ tokens.css ──var()──▶ Primitives ──▶ Components ──▶ Screens
 (primitive + semantic)  (generated)          (Stack, Text)   (BudgetCard)   (BudgetOverview)
```

Each arrow points one way. A screen knows components. A component knows primitives and semantic variables. Nothing knows a raw value except the primitive layer of `tokens.json`.

## Why two token layers
Primitives answer "what colors do we own?". Semantics answer "what is this color for?".

| Primitive | Semantic | Used by |
|---|---|---|
| `color.green.600` | `color.status.success` | BudgetCard status, progress bar |
| `color.red.600` | `color.status.danger` | BudgetCard over-budget state |
| `space.4` | `space.inset.md` | card padding |

A rebrand changes primitives. A dark theme remaps semantics. Components do not change in either case.

## Why CSS variables
- They work in every browser with no runtime library.
- Storybook, tests and the app read the same file.
- Themes are one more `:root[data-theme='dark']` block in `tokens.css`.

## Why presentational components
A designer owns how things look. An engineer owns what they do. Keeping fetch, state and formatting out of components means the designer can change any component file without touching behaviour, and the engineer can wire data without touching styling.

## Where Figma fits
Figma is one possible input to `tokens.json` and screen specs. It is not required. In this course the inputs are:
- a token JSON file you edit by hand
- markdown screen specs in `screens/`
- component specs from `templates/component-spec-template.md`

If a team has Figma, `/designer-extract` can turn a frame into the same markdown and token entries. The rest of the flow stays the same.

## What good looks like
- Delete `tokens.css`, run `npm run build:tokens`, nothing changes.
- Search the components folder for `#` or `px`: only `1px` borders show up.
- Every component has a story you can point a reviewer at.
