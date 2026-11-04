# Exercise 1: Brand to Tokens

**Time:** 60 to 75 minutes
**You produce:** `workspaces/designer/tokens/tokens.json` with a primitive layer and a semantic layer, where every text and background pair the app uses passes WCAG AA.

## Scenario

Northwind Co. is building **Northwind Expenses**, the internal app staff use to file expense claims. The brand team sent a one-page brief: two brand colors, neutrals, status colors, a type scale and a spacing rhythm. Nobody has turned it into tokens yet, and engineering will not start the components until there is a token file they can trust.

The catch: marketing wants Harbor Teal on the primary button, and some of the colors in the brief fail contrast when used as text. Your job is to keep the brand and pass AA.

## Inputs

| File | What it is |
|---|---|
| `inputs/brand-brief.md` | Brand colors, neutrals, status colors, type scale, spacing, radius, the contrast rule and the **token contract** (the semantic names the check reads) |
| `checks/pairs.json` | The 18 foreground / background pairs the app renders. Read it before you pick colors |

No Figma file is needed. The brief is the source of truth.

## Task

1. **Primitive layer.** One primitive token per approved color in the brief, plus the spacing, radius, border, font size, font weight and line height scales. Primitives hold raw values only.
2. **Semantic layer.** Every name in the brief's token contract table, each pointing at a primitive with a `{primitive.x.y}` reference. Add semantic tokens for spacing, type, radius and border width named by intent (`space.inset.md`, `font.size.label`, `radius.badge`).
3. **Pass contrast.** Every pair in `checks/pairs.json` passes: 4.5:1 for text, 3:1 for the focus ring and control borders.
4. **Write down the decisions.** In `workspaces/designer/plans/transitions/latest.md` (or the transition doc `/next-session` writes), list every place you moved away from the brief's suggestion and why, with the ratio. Example: "Primary button uses teal 700, not Harbor Teal 500: white on teal 500 is 4.12:1."

Format is the stack's format: every leaf has `$value` and `$type`, top level is exactly `primitive` and `semantic`. Look at `workspaces/designer/examples/budget-card/tokens/tokens.json` for the shape.

## Commands to use

```
/set-persona add designer
/setup-stack designer
/architect designer exercises/designer/01-brand-to-tokens/README.md
/start-session designer
/designer-extract exercises/designer/01-brand-to-tokens/inputs/brand-brief.md
/next-session
```

- `/architect` reads this README as the plan. Expect the interface contract to list the token set and a Phase 0 session that creates `tokens/tokens.json`.
- `/designer-extract` on the brief gives you a context doc with every value and every name the contract asks for. Use it as your checklist.
- Ask the agent to run the checks below after each change. Do not let it "fix" a failing pair by editing `pairs.json`.

## How it is checked

Run from the repo root:

```bash
# 1. Schema and references (the stack's token build, validate only)
cd workspaces/designer && npm run check:tokens && cd ../..
#    No package.json yet? Run the script directly:
#    node workspaces/designer/scripts/build-tokens.mjs --check
#    Script missing? Copy it from workspaces/designer/examples/budget-card/scripts/build-tokens.mjs

# 2. Contrast for every declared pair
node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs
#    Different token path:
#    node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs --tokens path/to/tokens.json
```

`check_contrast.mjs` has no dependencies. It resolves each semantic token through its reference to a hex value, computes the WCAG 2.x ratio, prints a table and exits 1 if any pair fails or any token is missing. A passing run ends with:

```
[contrast] OK: 18 pair(s) meet WCAG AA
```

## Done when

- [ ] `npm run check:tokens` (or `build-tokens.mjs --check`) prints `[tokens] OK`
- [ ] `check_contrast.mjs` exits 0 and prints `OK: 18 pair(s) meet WCAG AA`
- [ ] Every primitive color value appears in the brief. No invented hex values
- [ ] No semantic token holds a raw value. Every one is a `{primitive...}` reference
- [ ] Semantic names describe intent (`color.text.muted`), not appearance (`color.gray600`)
- [ ] The transition doc lists each brief suggestion you overrode, with the ratio that forced it
- [ ] `npm run build:tokens` writes `src/styles/tokens.css` and you did not edit that file by hand

## Stretch

- **Dark mode.** Save `tokens/tokens.dark.json` with the same primitives and a dark semantic layer (same names, new references), then run the checker against it with `--tokens`. Which brand colors survive on a dark surface?
- **Large text.** WCAG AA allows 3:1 for text 24px and up, or 18.66px bold and up. Add a pair to a copy of `pairs.json` for the page title on `color.surface.page` with `"min": 3` and pass it with `--pairs`. Is it worth a separate token?
- **Optional Figma path.** If your team keeps the palette in Figma, add the Figma MCP server (see `personas/designer/SETUP.md`) and run `/designer-extract <figma-frame-url>`. Check the values it returns against the brief before you trust them.
