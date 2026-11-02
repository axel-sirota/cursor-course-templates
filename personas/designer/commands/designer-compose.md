# /designer-compose

Assemble a working prototype from the design context produced by `/designer-extract` and the existing components.

Paths are relative to `workspaces/designer/`.

## Steps

1. **Load the design context.** Accept any of:
   - `docs/design-context-{screen-name}.md` (from `/designer-extract` on a screen spec)
   - `docs/figma-context-{frame-name}.md` (from `/designer-extract` on a Figma frame, optional)
   - A screen spec `screens/{screen-name}.md` directly, read together with `tokens/tokens.json`

   If several candidates exist, ask the user which screen or frame to implement before proceeding.

2. **Inventory existing components.** For each component listed in the context file:
   - Search the workspace (`src/components/`) for an existing match by name, file, or props signature.
   - If found: use it directly. Do not create a duplicate.
   - If not found: ask the user whether to (a) create a new component or (b) reuse the closest existing one with minor adjustments. Do not decide unilaterally.

3. **Apply layout.** Using the layout description from the context file:
   - Apply flex/grid structure using existing layout utilities or CSS classes already present in the workspace.
   - Apply spacing using design tokens from `tokens/tokens.json` (or the generated `src/styles/tokens.css`). Never hardcode pixel values.

4. **Wire up handlers.** For any interactive element (button, input, link):
   - Add an empty handler stub (e.g. `onClick={() => {}}`) with a `// TODO: engineering` comment.
   - Do NOT invent business logic, make API calls, or add state management.

5. **Output.** A working component or page file plus a summary listing:
   - Components reused (with file paths)
   - Tokens applied (with token names)
   - Stubs left for engineering (with file+line references)

## Constraints (enforced by `000-designer-workflow.mdc`)

- No hardcoded color, spacing, font, or radius values. Every value must reference a token.
- No inline `style={{ }}` attributes. Use `className` with token-backed classes.
- No modification of existing event handlers, API calls, routes, or state management files.
- Existing logic files (reducers, stores, API modules) are read-only in this command.

## Notes

- If a token referenced in the context file does not exist in `tokens/tokens.json`, flag it and ask the user before inventing a new token name.
- If `docs/` does not exist in the workspace, create it before writing any output files.
- Run `token-validator` subagent after composing to verify no hardcoded values slipped in.
