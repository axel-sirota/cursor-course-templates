# /designer-extract

Pull design tokens, components, and layout into a context file for `/designer-compose`. The default source is the token JSON plus a markdown screen spec. A Figma frame via MCP is the optional source.

Paths are relative to `workspaces/designer/`.

## Steps

1. **Get the source.** Ask the user for one of:
   - **Default (no Figma):** a screen spec `screens/{screen-name}.md`, read together with `tokens/tokens.json`
   - **Optional (Figma):** a Figma file/frame URL (e.g. `https://www.figma.com/file/ABC123/...?node-id=1%3A2`) or a frame node ID (e.g. `1:2`)

   If none is provided and none is in the current context, prompt: "Which screen spec in `screens/` should I extract? (Or paste a Figma frame URL if you have one.)"

2. **Extract.**
   - **Screen spec path:** read the spec and `tokens/tokens.json` directly. List every semantic token the screen needs (colors, spacing, typography, radius, shadow), every component it names and the variants it implies, the layout structure (flex direction, alignment, gap, padding), and any assets. Flag anything the spec asks for that has no token. Save to `docs/design-context-{screen-name}.md`.
   - **Figma path:** delegate to the `figma-extractor` subagent with the URL or node ID. It fetches tokens, component instances and variants, layout and asset URLs, and saves to `docs/figma-context-{frame-name}.md`.

3. **Report results.** Summarize:
   - Path to the saved context file
   - Token count extracted
   - Component count extracted
   - Asset count extracted
   - Any inconsistencies flagged (e.g. values in the spec or Figma file with no matching token)

## Output

A markdown file at `docs/design-context-{screen-name}.md` (spec source) or `docs/figma-context-{frame-name}.md` (Figma source) containing:
- Token table (token name → value → category)
- Component variant matrix (component name → variants present)
- Layout description (hierarchy, flex/grid structure, spacing)
- Asset URLs or paths with suggested local paths

This file is the primary input to `/designer-compose`.

## Notes

- Do not write any component implementation. This command produces the context file only.
- If `docs/` does not exist in the workspace, create it before writing the output file.
- If the Figma MCP server is unreachable, fall back to the screen spec path, or point the user to the optional Figma section of `personas/designer/SETUP.md`.
