# Project Context: Designer, React + Design Tokens

## Architecture Shape
Design System (Tokens → Primitives → Components → Screens)

- **Tokens**: `tokens/tokens.json` holds two layers. The `primitive` layer is the raw palette and scales. The `semantic` layer names intent (`color.surface.card`, `space.inset.md`) and references primitives.
- **Primitives**: small building blocks (Stack, Text, Surface) that read semantic CSS variables only.
- **Components**: product parts (BudgetCard, CategoryRow) composed from primitives. Presentational only. Props in, markup out.
- **Screens**: markdown specs in `screens/` that say which components sit where. A screen file in `src/screens/` only arranges components.

Source of truth for this course is the token JSON plus markdown screen specs. Figma MCP is optional. When a Figma frame exists, `/designer-extract` can read it. When it does not, the token file and the screen spec are enough.

## Tech Stack
- **Language**: TypeScript 5.9 (strict mode)
- **UI library**: React 18.3
- **Build / dev server**: Vite 5.4 with `@vitejs/plugin-react` 4.7
- **Component catalogue**: Storybook 8.6 (`@storybook/react-vite`)
- **Tests**: Vitest 2.1 + Testing Library (`@testing-library/react` 16, `@testing-library/jest-dom` 6) on jsdom 25
- **Accessibility check**: `axe-core` 4 run inside each component test
- **Token pipeline**: `scripts/build-tokens.mjs` (plain Node 20+, no dependencies) turns `tokens/tokens.json` into `src/styles/tokens.css` CSS variables
- **Optional**: Style Dictionary 4 when the team needs iOS / Android outputs. The JSON format (`$value`, `$type`) already matches the W3C Design Tokens draft, so the swap is a config change.
- **Optional**: Figma Dev Mode MCP for teams that have a Figma file.

## Vibe & Style
- **Naming**: components in PascalCase (`BudgetCard.tsx`). CSS classes in kebab-case with a component prefix (`budget-card__amount`). Tokens in dot paths (`color.text.muted`), CSS variables in kebab-case (`--color-text-muted`).
- **One folder per concern**: `tokens/`, `src/styles/`, `src/components/`, `src/screens/`, `screens/` (specs).
- **Co-located files**: each component ships with `X.tsx`, `X.css`, `X.test.tsx`, `X.stories.tsx`.
- **State through attributes**: variants are `data-*` attributes (`data-status="over"`), styled in CSS. No class name juggling in JSX.

## Key Rules
- **Semantic tokens over primitives.** Components read `--color-*`, `--space-*`, `--font-*`, `--radius-*`. They never read `--primitive-*` variables.
- **No hardcoded values.** No hex, `rgb()`, `hsl()` or named colors. No px, rem or em for spacing, font size, radius or shadow. Everything is `var(--token)`.
- **No inline styles.** No `style={{ }}` in JSX. Dynamic values go through native elements (`<progress>`, `<meter>`) or `data-*` attributes.
- **Logic stays out of presentational components.** No fetch, no state stores, no number formatting, no business rules. The parent passes ready-to-render props.
- **Generated files are not edited by hand.** `src/styles/tokens.css` is rebuilt from `tokens/tokens.json` with `npm run build:tokens`.
- **New token = spec change.** A missing token is written into `tokens/tokens.json` first, with a reason in the transition doc. Never invent a value inside a component.

## Workspace Layout
```
workspaces/designer/
├── tokens/
│   └── tokens.json            # primitive + semantic layers (source of truth)
├── scripts/
│   └── build-tokens.mjs       # tokens.json → src/styles/tokens.css (+ --check)
├── screens/
│   └── <screen-name>.md       # screen specs (layout, components, states)
├── src/
│   ├── styles/tokens.css      # GENERATED, do not edit
│   ├── components/
│   │   ├── X.tsx
│   │   ├── X.css
│   │   ├── X.test.tsx
│   │   └── X.stories.tsx
│   ├── screens/               # composed screens, arrangement only
│   └── test/setup.ts
├── .storybook/                # main.ts + preview.ts (imports tokens.css)
├── plans/                     # interface-contract.md, sessions/, transitions/
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Entry Point & Structure
- **Token build**: `npm run build:tokens` (runs `node scripts/build-tokens.mjs`)
- **Token check**: `npm run check:tokens` (schema and reference check, no output written)
- **Tests**: `npm test` (Vitest: render + accessibility per component, token check)
- **Catalogue**: `npm run storybook` (port 6006)
- **Type check**: `npm run typecheck`
- **Worked example**: `examples/budget-card/`

## Active Phase
- Current: Phase 0 (Skeleton: tokens.json, placeholder components, one story each)
