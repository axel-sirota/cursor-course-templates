# Lab 7 solution — Scope the Checkout (sparse worktrees)

Source lab: `materials/fragments/sparse-checkout.html` (Demo 7 is the Easy tier's
template; the sample monorepo intentionally ships without `sparsePaths` — this lab
adds it).

- **Easy:** configure `sparsePaths` so a payments worktree checks out only what payments work needs, then verify the worktree contents directory by directory against a written prediction.
- **Hard:** deliberately omit `.claude` from the list, observe what breaks in the worktree session, diagnose it, fix the list, and show the session behaving correctly.

## Easy solution

The thinking step first: what does payments work actually need?

- `services/payments` — the code under change.
- `contracts` — the schemas the Stop-hook validator reads; without them
  `validate.sh` dies.
- `.claude` — settings, hooks (`path_guard.py`, `agent_activity.py`), agents; rule 3
  says a root-level *directory* only exists if listed.
- Nothing else: `specs/` is nice-to-have reading, `services/gateway` and
  `services/notifications` are exactly what we want off disk.

Edit `.claude/settings.json` so the `worktree` block reads:

```json
{
  "worktree": {
    "baseRef": "head",
    "symlinkDirectories": [".venv"],
    "sparsePaths": [".claude", "services/payments", "contracts"]
  }
}
```

Restart `claude`, spawn a worktree agent on a payments pretext task ("add a docstring
to services/payments — I want to inspect its checkout"), then verify from a second
terminal. Real outputs — agent-created worktree from the captured Demo 7 run
(`materials/captured/demo7-du.txt`), cross-checked 2026-07-24 by creating the same
sparse checkout with git directly (`git worktree add --no-checkout` +
`git sparse-checkout set --cone .claude services/payments contracts`):

```text
$ git worktree list        # find $WT = .claude/worktrees/agent-<id>
$ ls -A "$WT"
.claude  .env  .gitignore  .venv  .worktreeinclude
CHANGELOG.md  CLAUDE.md  README.md  contracts  init.sh  services

$ ls -A "$WT/services"
payments          # notifications/ and gateway/ are NOT on disk

$ git -C "$WT" sparse-checkout list
.claude
contracts
services/payments

$ ls "$WT/specs"
ls: .../specs: No such file or directory
```

Score the prediction against the three rules: root-level *files* (`init.sh`,
`.gitignore`, `CHANGELOG.md`, `README.md`, root `CLAUDE.md`) came along for free;
`.env` arrived via `.worktreeinclude` and `.venv` via `symlinkDirectories` (both are
Claude Code machinery — a bare git sparse worktree has neither); `specs/` and the two
unlisted services simply do not exist.

Size check (2026-07-24, scratch copy; BSD `du` uses `-I`, GNU uses `--exclude`):

```text
$ du -sh -I .venv -I .git .        # main checkout, working files only
1.1M    .
$ du -sh "$WT"
144K    <worktree>
```

About 8x smaller on a deliberately tiny repo; the ratio is the lesson, and it grows
with every package a real monorepo adds.

## Hard solution

Set the list to `["services/payments", "contracts"]` (`.claude` omitted), restart,
and spawn a fresh worktree agent. What is on disk (real output, git-level sparse
worktree without `.claude`, 2026-07-24):

```text
$ ls -A "$WT"
.git  .gitignore  .worktreeinclude
CHANGELOG.md  CLAUDE.md  README.md  contracts  init.sh  services

$ ls "$WT/.claude"
ls: .../.claude: No such file or directory
```

Diagnosis to elicit from students — everything project-level that lives under
`.claude/` is missing in the worktree session:

- `settings.json` is gone: the `permissions.deny` rules (`dist/`, `build/`,
  `__pycache__/` reads) no longer apply, and the `PostToolUse` `agent_activity` hook
  is not registered — the agent's tool calls stop appearing in
  `logs/tool_usage.jsonl`, which is usually the first symptom students notice.
- `.claude/hooks/path_guard.py` is gone: an agent whose frontmatter wires the guard
  has a hook command pointing at a file that does not exist in its checkout. The
  write-fence the whole module relies on silently stops guarding.
- `.claude/agents/` and `.claude/commands/` are gone: no agent definitions, no
  `/catchup`, no `/implement-across-services` inside that worktree.

The failure is quiet, not loud — nothing errors at spawn time; protections are just
absent. That is why the fragment calls `.claude` the one path you must never leave
off the list.

Fix: restore `".claude"` as the first entry, restart, respawn. The worktree now shows
`.claude` in `ls -A` and `git -C "$WT" sparse-checkout list`, the activity log
resumes, and the hooks fire again — same checks as the Easy tier.

Afterwards have students revert `settings.json` (or commit the Easy-tier list
deliberately): later labs assume the shipped settings shape.

## What students get wrong

1. **Leaving `.claude` off the list without noticing** (the Hard tier makes it
   deliberate, but students do it accidentally in the Easy tier too). Nothing
   crashes; hooks, deny rules, and commands are just missing in every worktree. If a
   worktree session behaves "less guarded" than the main one, check
   `ls "$WT/.claude"` first.
2. **Expecting `specs/` or another root directory to be present.** Rule 3 cuts both
   ways: root files come along, root *directories* do not. An agent that needs the
   spec must have `specs` on the list — remember the list is one union shared by
   every worktree in the session (rule 2), so adding it affects all agents.
3. **Testing the change without restarting the session.** `sparsePaths` is read at
   session start; a list edited mid-session produces a worktree with the old shape
   and students conclude the setting does nothing. Restart `claude` after every
   settings change.

Verified: 2026-07-24 against sample-monorepo/python-fastapi
