# PM PRD Starter

How to start a PRD in this workspace. Every path is relative to the workspace root.

## 1. Set up the workspace (once)

```bash
mkdir -p prds stories research decisions docs scripts
cp examples/budget-alerts/scripts/check_prd.py scripts/
cp examples/budget-alerts/.markdownlint-cli2.jsonc .
touch glossary.md
```

Check that the tools run:

```bash
npx markdownlint-cli2@0.18.1
python3 scripts/check_prd.py examples/budget-alerts --strict
```

The second command must print `OK`. If it does, the checker works on a known-good PRD.

## 2. Create the PRD skeleton

```bash
cp templates/prd-template.md prds/<feature-slug>.md
```

- Replace the H1 with `# PRD: <Feature name>`.
- Leave every `TODO:` in place for now. The skeleton is done when every heading exists.
- Run `python3 scripts/check_prd.py .`. It passes with a warning: "no story files yet".

## 3. Fill Discover sections

Write these four, in order, before any story:

1. **Problem**: one paragraph, one number, one cited research file.
2. **Goals**: `G1`, `G2`, each with baseline, target, time window.
3. **Non-goals**: at least two, each with a reason.
4. **Users**: named roles, one line of context each.

Put raw notes in `research/<YYYY-MM-DD>-<source>.md`. Quote numbers from there, not from memory.

## 4. Add epics and stories

1. Add rows to the Epics table. Each epic names one goal.
2. For each story:

   ```bash
   cp templates/story-template.md stories/<feature-slug>-01-<story-slug>.md
   ```

3. Fill the story line, AC, edge cases and INVEST table.
4. Add one row per story to the PRD User Stories index, with a relative link to the file.

## 5. Finish the PRD

- Fill all six NFR subsections with a number or a named standard.
- List edge cases by ID and point each at a story.
- Fill Dependencies, Rollout Plan, Success Metrics, Open Questions.
- Add every domain term to `glossary.md`.

## 6. Check, validate, decompose

```bash
npx markdownlint-cli2@0.18.1
python3 scripts/check_prd.py . --strict
```

Then in Cursor:

```text
/pm-validate prds/<feature-slug>.md
/pm-decompose prds/<feature-slug>.md
```

Do not run `/pm-decompose` until the validation report says "Ready to decompose: Yes".

## Reference

Read `examples/budget-alerts/` end to end before writing your first PRD. It passes every check in this stack.
