# /designer-handoff

Generate a PR description and reviewer checklist for visual changes, ready for engineering review.

## Steps

1. **Identify changed files** — Run `git diff main...HEAD --stat` to list all modified files. Categorize them:
   - **Visual changes:** component files, style files, token files
   - **Tokens used:** list each design token referenced in changed files
   - **Components reused:** list each existing component incorporated
   - **Logic preserved:** confirm that no handler, route, API module, reducer, or state management file was modified. If any logic file appears in the diff, flag it prominently before continuing.

2. **Capture responsive screenshots** — Run the `responsive-checker` subagent to capture breakpoint screenshots at 375×667 (mobile), 768×1024 (tablet), and 1440×900 (desktop). Screenshots are saved to `docs/responsive/`.

3. **Generate `PR_DESCRIPTION.md`** — Write the file to the repo root (or `docs/`) with the following sections:

   ```markdown
   ## What changed
   - (2–4 bullets describing visual changes at the component/page level)

   ## What was preserved
   - (explicit list of logic files that were NOT modified)

   ## Screens to review
   - Mobile (375×667): docs/responsive/mobile-{page}.png
   - Tablet (768×1024): docs/responsive/tablet-{page}.png
   - Desktop (1440×900): docs/responsive/desktop-{page}.png

   ## Designer QA checklist
   - [ ] Visual matches Figma frame (link to source frame)
   - [ ] All breakpoints render without overflow or truncation
   - [ ] All values reference design tokens (no hardcoded colors/spacing)
   - [ ] No logic files modified (handlers, routes, state)
   - [ ] Empty handler stubs marked with // TODO: engineering
   ```

4. **Report** — Print the path to `PR_DESCRIPTION.md` and remind the user to attach the responsive screenshots when opening the PR.

## Notes

- If `git diff main...HEAD` shows no changes, warn the user and ask whether to compare against a different base branch.
- If responsive screenshots could not be captured (Playwright not available), note "screenshots pending" in the PR description and add a checklist item for the reviewer to verify manually.
- Do not push or open the PR — leave that to the engineer or the user.
