# Session 11 — Phase G: Universal Commands Persona-Aware Branches

**Phase:** G
**Goal:** Add persona-aware branches to 6 universal commands. They read `## Active Persona` from context and adjust behavior. No commands are removed or replaced — only extended.
**Depends on:** Session 10 (`set-persona` must write Active Persona to context before these branches can be tested)
**Parallel with:** Session 12 — gitignore and client scaffold are independent of command updates
**Next session:** Session 12 (gitignore + client scaffold)

---

## Files to Update

```
.cursor/commands/architect.md       ← ADD persona branch near top
.cursor/commands/start-session.md   ← ADD persona branch
.cursor/commands/start-project.md   ← ADD persona branch
.cursor/commands/code-review.md     ← ADD persona branch
.cursor/commands/next-session.md    ← ADD persona branch
.cursor/commands/read.md            ← ADD persona branch

.claude/commands/architect.md       ← identical updates (mirror)
.claude/commands/start-session.md
.claude/commands/start-project.md
.claude/commands/code-review.md
.claude/commands/next-session.md
.claude/commands/read.md
```

---

## Change Pattern

Insert a **Persona Detection Block** at the top of each command's Execution Flow, before any existing steps. This block reads `## Active Persona` and routes to a persona-specific preamble. If no persona is set, the existing engineer-flavored behavior runs unchanged (backwards compat).

**Template for the Persona Detection Block:**

```markdown
## Persona Detection (run first)

Read the active persona from context:
- Cursor: `.cursor/context.md` — look for `## Active Persona`
- Claude Code: `CLAUDE.md` — look for `## Active Persona`

If section missing or value is empty → treat as `engineer` (backwards compatible default).

Branch to the appropriate preamble below, then continue with the standard execution flow.
```

---

## Per-Command Persona Branches

### `architect.md` — Persona Preambles

**engineer:** "Design the API surface for a backend feature. Output: OpenAPI spec or route list, data model, skeleton implementation plan."

**designer:** "Design the component hierarchy for a visual feature. Output: component tree (which components exist vs need creating), token requirements, layout structure. No API design — assume API already exists or will be provided by engineering."

**pm:** "Draft the PRD structure for a product feature. Output: goals + non-goals, user personas affected, list of user stories (INVEST format), NFR categories to address. No implementation detail — that is engineering's job."

**data-scientist:** "Design the experiment plan for a data science problem. Output: data sources needed, EDA hypotheses to test, candidate model types, success metrics, validation approach. No code yet — this is the design phase before `/ds-explore`."

### `start-session.md` — Persona Preambles

**engineer:** Load active stack from context + active rules. Show: current stack, active phase, last session summary if present. Ask for session goal.

**designer:** Load active Figma context file if present (`docs/figma-context-*.md`). Show: active design tokens summary, last session's prototype state. Ask which frame or component to work on today.

**pm:** Load active PRD if present (`prds/` or `docs/`). Show: PRD title, story count, validation status. Ask which epic or story to focus on today.

**data-scientist:** Load active EDA doc + experiment log. Show: dataset in use, last experiment's metrics, next hypothesis to test. Ask for today's experiment goal.

### `start-project.md` — Persona Preambles

**engineer:** Propose data entities, REST API endpoints, and implementation phases for the described domain.

**designer:** Propose a component library inventory for the described UI: which components exist in the codebase, which need building, what tokens they require.

**pm:** Propose an initial user story map: key user roles, their goals, and an ordered list of epics with rough priority.

**data-scientist:** Propose a data pipeline design: input data sources, feature engineering steps, candidate model approaches, evaluation strategy.

### `code-review.md` — Persona Preambles

**engineer:** Security (secret leaks, injection), style (naming, types), testing (coverage, assertion quality). Use `code-reviewer` and `security-auditor` subagents if available.

**designer:** Token discipline (no hardcoded values), logic preservation (no handler/route/state changes), responsive behavior (breakpoints). Use `token-validator` subagent if available.

**pm:** INVEST compliance (all stories), Given/When/Then format (all ACs), NFR completeness. Use `gap-detector` subagent if available.

**data-scientist:** Reproducibility (seed set, requirements pinned, no absolute paths), experiment logging (all runs tracked), model card completeness. Use `reproducibility-checker` subagent if available.

### `next-session.md` — Persona Preambles

**engineer:** Check test status (run `test-runner` subagent if available). Advance `## Active Phase` in context if phase AC are met. Generate transition doc with: session status, where stopped, next immediate step, files to load.

**designer:** Prompt for screenshot comparison via `responsive-checker` if not yet done. Update Figma context doc if design changed. Generate transition doc with: components changed, open style questions, next frame to implement.

**pm:** Run `gap-detector` on active PRD if not yet run this session. Update story count in context. Generate transition doc with: stories validated, stories remaining, next three to work on.

**data-scientist:** Invoke `experiment-tracker` to log session results if not yet done. Update experiment log summary in context. Generate transition doc with: hypothesis tested, metrics achieved, next experiment to run.

### `read.md` — Persona Preambles

**engineer:** Read context (stack + phase) + active rules + last session transition doc. Output: Stack, Current Phase, Active Rules count, Next Step.

**designer:** Read context (active persona) + active Figma context doc (if present). Output: Active Persona, Figma frame in progress, last iteration summary.

**pm:** Read context + active PRD (if present). Output: Active Persona, PRD title, story count, validation status.

**data-scientist:** Read context + active EDA doc + experiment log tail. Output: Active Persona, Dataset, Last experiment metrics, Next hypothesis.

---

## Implementation Note

Each branch is a markdown section added to the existing command file. The existing execution flow steps remain UNCHANGED after the preamble. The preamble only sets context for how the AI should interpret the session — it does not replace the mechanical steps.

Update BOTH `.cursor/commands/` and `.claude/commands/` for each file. Content is identical.

---

## Acceptance Criteria

- [ ] All 6 command files in both `.cursor/commands/` and `.claude/commands/` contain a `## Persona Detection` section at the top of their execution flow
- [ ] Each command has branches for all 4 personas + fallback to engineer default
- [ ] Existing engineer behavior unchanged when `## Active Persona` is not set (backwards compat)
- [ ] `architect` branches output the correct deliverable type per persona (API surface vs component tree vs PRD vs experiment plan)
- [ ] `code-review` branches invoke the correct subagents per persona
- [ ] The 4 commands that stay universal (`setup-stack`, `detect-stack`, `dockerize`, `research`) are NOT modified
