# Lab 4 solution — Your Own Numbers (token-budget measurement)

Source lab: `materials/fragments/token-budget.html` (Demo 4 is the template for the Easy tier).

- **Easy:** measure the Memory-files category on `flat-claude-md` and on `main` (after `/clear`, before touching any service) and compute the percentage saving.
- **Hard:** trigger a nested `CLAUDE.md` load on `main`, `/compact` it away, prove the loss from `/context`, then recover it with `/clear` + `/catchup`.

## Easy solution

Run both measurements on the student's initialized copy (`~/labs/refund-monorepo`; the reference run below used the instructor scratch copy at `/private/tmp/refund-monorepo`).

Flat layout first:

```bash
cd ~/labs/refund-monorepo
git checkout flat-claude-md
claude
```

```text
> /clear
> /context
```

Real output (re-run on 2026-07-24, claude 2.1.218 — print-mode equivalent
`claude -p --setting-sources project,local "/context"`, which excludes user-level
memory so the numbers show only what the repo layout costs):

```text
| Category      | Tokens | Percentage |
| Memory files  | 2.6k   | 0.3%       |

### Memory Files
| Type    | Path                                   | Tokens |
| Project | /private/tmp/refund-monorepo/CLAUDE.md | 2.6k   |
```

One entry: the fat root file, all three services' rules loaded up front whether the
session needs them or not.

Nested layout second:

```bash
git checkout main
claude
```

```text
> /clear
> /context
```

Real output, same day, same machine:

```text
| Category      | Tokens | Percentage |
| Memory files  | 817    | 0.1%       |

### Memory Files
| Type    | Path                                   | Tokens |
| Project | /private/tmp/refund-monorepo/CLAUDE.md | 817    |
```

Root `CLAUDE.md` only — `services/*/CLAUDE.md` all exist on disk, none are loaded.

The number the lab asks for:

```text
saving = (2600 - 817) / 2600 = 68.6%  →  "about 69% on the Memory-files category"
```

Students' absolute numbers will differ (their user-level memory and MCP servers load
too); the ratio between the two runs on one machine is the honest measurement. Anyone
whose two numbers are identical almost certainly measured the same branch twice —
have them run `git branch --show-current` inside the session with `!`.

## Hard solution

All on `main`. Keep the Demo 3 `InstructionsLoaded` hook registered in
`.claude/settings.local.json` for this tier — it is the reliable witness (see the
caveat below).

```text
> Read services/payments/README.md and summarize the service in two sentences.
> /context
```

The read triggers the lazy load. Evidence from the real run
(`materials/captured/demo3-instructions-log.txt`):

```text
{…,"hook_event_name":"InstructionsLoaded","file_path":".../services/payments/CLAUDE.md",
 "memory_type":"Project","load_reason":"nested_traversal",
 "trigger_file_path":".../services/payments/README.md"}
```

Now generate enough conversation to make compaction meaningful (a few more reads or
small edits), then:

```text
> /compact
> /context
```

After `/compact`, the Memory Files table lists the root `CLAUDE.md` only — it is
re-injected from disk. `services/payments/CLAUDE.md` is gone as a live file; whatever
of it survives is paraphrase inside the compaction summary. That is the loss the
fragment's warning table describes.

Recover:

```text
> /clear
> /catchup
> /context
```

`/catchup` (shipped in `.claude/commands/catchup.md`) diffs the branch, re-reads the
changed files, and re-reads the `CLAUDE.md` of each service whose files appear in the
diff — re-triggering the lazy load as a real file, not summary residue. The hook log
gains a fresh `nested_traversal` entry for `services/payments/CLAUDE.md`; that entry
is the proof it is back.

**Observed CLI caveat (2.1.218, from the captured runs — see
`materials/captured/demo4-context-after.txt`):** in a continued print-mode session the
lazily loaded file does not reappear as its own row in the `/context` Memory Files
table; its tokens are carried in the Messages category (Messages grew 8 → 4.2k after
the read in the captured run). Interactive sessions behave better, but teach students
to treat the `InstructionsLoaded` hook log as the source of truth and `/context` as
the budget view.

## What students get wrong

1. **No `/clear` before a `/context` reading.** The Messages category from earlier
   turns contaminates the comparison and both branches look the same. Every reading
   in this lab starts with `/clear`.
2. **Comparing across machines or setups.** One student measures with three MCP
   servers loaded, another with none, and they argue about whose "saving" is right.
   The delta is only meaningful between two runs on the same machine, same session
   sources.
3. **Looking for the recovered file in the wrong place.** After `/catchup`, students
   stare at the Memory Files table, see only the root file, and conclude recovery
   failed — when the hook log already shows the `nested_traversal` re-load. Point
   them at `instructions-loaded.log`.

Verified: 2026-07-24 against sample-monorepo/python-fastapi
