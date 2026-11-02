# /designer-iterate

Refine a composed prototype using Cursor's browser panel / Design Mode in an interactive loop.

Paths are relative to `workspaces/designer/`. Edit only files inside that folder.

## Steps

1. **Confirm the running URL.** Ask the user for the local dev server URL. Default: the Vite dev server `http://localhost:5173`, or Storybook `http://localhost:6006` for a single component. If the dev server is not running, remind the user to start it from `workspaces/designer/` (`npm run dev`, `npm run storybook`, or equivalent) before continuing.

2. **Open the browser panel / Design Mode.** Instruct the user to open Cursor's browser panel (or use the Playwright MCP browser) and navigate to the URL confirmed in step 1.

3. **Iterate loop.** Repeat until the user is satisfied or until the user explicitly ends the loop:
   a. The user clicks an element and describes a change in plain language (e.g. "make this button primary blue, larger padding").
   b. Translate the description to a code change using design tokens. Never hardcode values.
   c. Apply the change to the source file.
   d. Confirm hot reload reflects the change (or instruct the user to refresh if hot reload is not configured).
   e. Ask: "Does this match the intent? Continue iterating or move on?"

4. **Suggest responsive check.** After 3 to 5 iterations, proactively suggest: "You've made several visual changes. Would you like to run the `responsive-checker` agent now to verify breakpoints before continuing?"

## Notes

- This is an interactive loop. No command argument is required.
- All changes must follow the same constraints as `/designer-compose`: no hardcoded values, no inline styles, no logic modifications.
- If the user requests a change that touches a handler, route, or state file, decline and note: "That change is in the logic layer. Add it to the engineering handoff stubs."
- After the loop ends, suggest running `/designer-handoff` to document the changes for PR review.
