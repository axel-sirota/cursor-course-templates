# /designer-extract

Pull design tokens, components, and layout from a Figma file via MCP and save the context for use by `/designer-compose`.

## Steps

1. **Get the Figma reference** — Ask the user for either:
   - A Figma file/frame URL (e.g. `https://www.figma.com/file/ABC123/...?node-id=1%3A2`)
   - A frame node ID directly (e.g. `1:2`)

   If neither is provided and no Figma URL is in the current context, prompt: "Please paste the Figma frame URL or node ID you want to implement."

2. **Delegate to `figma-extractor` subagent** — Pass the URL or node ID. The subagent will:
   - Fetch all design tokens (colors, spacing, typography, radius, shadow) from the frame
   - Enumerate all component instances and their variants
   - Describe the layout structure (flex direction, alignment, gap, padding)
   - Collect asset URLs (icons, images)
   - Save the extracted context to `docs/figma-context-{frame-name}.md`

3. **Report results** — After the subagent completes, summarize:
   - Path to the saved context file
   - Token count extracted
   - Component count extracted
   - Asset count extracted
   - Any inconsistencies flagged (e.g. hardcoded values found inside the Figma file itself)

## Output

A markdown file at `docs/figma-context-{frame-name}.md` containing:
- Token table (token name → value → category)
- Component variant matrix (component name → variants present in frame)
- Layout description (hierarchy, flex/grid structure, spacing)
- Asset URLs with suggested local paths

This file is the primary input to `/designer-compose`.

## Notes

- Do not write any component implementation — this command produces the context file only.
- If `docs/` does not exist, create it before writing the output file.
- If the Figma MCP server is unreachable, instruct the user to verify the Figma desktop app is running with Dev Mode MCP enabled (see `SETUP.md`).
