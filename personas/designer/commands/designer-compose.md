# /designer-compose

Assemble a working prototype from the Figma context produced by `/designer-extract` and the existing codebase components.

## Steps

1. **Load the Figma context** — Read `docs/figma-context-{frame-name}.md`. If multiple context files exist, ask the user which frame to implement before proceeding.

2. **Inventory existing components** — For each component listed in the context file:
   - Search the codebase for an existing match by name, file, or props signature.
   - If found: use it directly — do not create a duplicate.
   - If not found: ask the user whether to (a) create a new component or (b) reuse the closest existing one with minor adjustments. Do not decide unilaterally.

3. **Apply layout** — Using the layout description from the context file:
   - Apply flex/grid structure using existing layout utilities or CSS classes already present in the codebase.
   - Apply spacing using design tokens from `tokens.json`, `theme.ts`, or equivalent — never hardcode pixel values.

4. **Wire up handlers** — For any interactive element (button, input, link):
   - Add an empty handler stub (e.g. `onClick={() => {}}`) with a `// TODO: engineering` comment.
   - Do NOT invent business logic, make API calls, or add state management.

5. **Output** — A working component or page file plus a summary listing:
   - Components reused (with file paths)
   - Tokens applied (with token names)
   - Stubs left for engineering (with file+line references)

## Constraints (enforced by `000-designer-workflow.mdc`)

- No hardcoded color, spacing, font, or radius values — every value must reference a token.
- No inline `style={{ }}` attributes — use `className` with token-backed classes.
- No modification of existing event handlers, API calls, routes, or state management files.
- Existing logic files (reducers, stores, API modules) are read-only in this command.

## Notes

- If a token referenced in the Figma context does not exist in the codebase token file, flag it and ask the user before inventing a new token name.
- If `docs/` does not exist, create it before writing any output files.
- Run `token-validator` subagent after composing to verify no hardcoded values slipped in.
