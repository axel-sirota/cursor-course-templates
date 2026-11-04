# Exercise 2: Fix the Flawed PRD

**Time:** 60 to 75 minutes
**Needs:** Exercise 1 done (the workspace has `research/` with the Northwind files)
**You produce:** a fixed `prds/expense-fast-track.md` with its stories, plus `docs/defects-expense-fast-track.md`: every defect you found, with file and line, and the fix.

## Scenario

A PM on another squad wrote "Expense Fast Track" in a rush before going on leave. Engineering wants to start sizing it on Monday. You own it now. Before anyone decomposes it, you review it like a Three Amigos session would: is every story INVEST, is every acceptance criterion testable, does it match the expense policy, and does it stay in scope?

The draft has seeded defects. Some are structural (a script can find them). Most need judgment. Find as many as you can, then fix them.

## Inputs

| File | What it is |
|---|---|
| `inputs/prds/expense-fast-track.md` | the draft PRD |
| `inputs/stories/expense-fast-track-01-*.md` to `-06-*.md` | six story files, one per story |
| `inputs/glossary.md` | glossary for this PRD |
| `../../_data/northwind/expense_policy.json` | the real expense policy. Amounts are in cents (`7500` = $75.00) |
| `../../_data/northwind/support_tickets.csv` | October ticket sample, for checking the PRD's claims |
| `../../_data/northwind/interview_notes.md` | six user interviews (P1 to P6) |

The folder layout (`prds/`, `stories/`, `glossary.md`) matches the workspace, so the structure checker runs on `inputs/` as is.

## Setup

```bash
cp exercises/pm/02-fix-the-flawed-prd/inputs/prds/expense-fast-track.md workspaces/pm/prds/
cp exercises/pm/02-fix-the-flawed-prd/inputs/stories/expense-fast-track-*.md workspaces/pm/stories/
cp exercises/_data/northwind/expense_policy.json workspaces/pm/research/   # skip if done in exercise 1
```

Open `inputs/glossary.md` and paste its `##` entries into `workspaces/pm/glossary.md` (keep one H1).

## Task

1. **Read before you run anything (15 minutes).** Read the PRD and all six stories yourself. Write your own defect list in `docs/defects-expense-fast-track.md` as a table: `# | File | Line | Defect | Rule broken | Fix`. Check every number against `expense_policy.json`.
2. **Run the agent review.** Run `/pm-validate prds/expense-fast-track.md`. Add anything it found that you missed. Mark each row with who found it: `me`, `agent`, or `both`.
3. **Optional: run the script.** If you have Python 3.11+, run the structure checker (see "How it is checked"). Mark the rows it also catches. Write one sentence on what kind of defect a script can never catch.
4. **Fix the PRD and stories.** Rules for fixing:
   - Split a story that is too big. New stories get the next unused ID (EFT-07, EFT-08 and so on). Never reuse an ID.
   - Rewrite implementation-led stories from the user's point of view, or delete them and say why in the defect table.
   - Every AC is Given/When/Then with real values and one observable outcome per Then.
   - Every goal has a baseline, a target and a time window. Every NFR has a number or a named standard.
   - Out-of-scope work moves to Non-goals with a reason. Delete its story file and its epic.
   - Policy numbers come from `expense_policy.json`, not from memory.
5. **Re-validate.** Run `/pm-validate` again until the verdict is "Ready to decompose? Yes".
6. **Decompose and report.** Run `/pm-decompose prds/expense-fast-track.md`, then `/pm-report`.

## Commands to use

```
/start-session pm
/pm-validate prds/expense-fast-track.md      # before your fixes: compare with your own list
/pm-validate prds/expense-fast-track.md      # after your fixes: must say "Ready to decompose? Yes"
/pm-decompose prds/expense-fast-track.md     # docs/tickets-<epic>.md
/pm-report                                   # docs/status-<date>-<epic>.md
/next-session
```

You do not need `/architect` for this exercise. The PRD already exists.

## How it is checked

1. **`/pm-validate`** (the main check). The "after" run says "Ready to decompose? Yes" with no Critical findings and no logged overrides.
2. **Instructor key.** Your `docs/defects-expense-fast-track.md` is compared with the key. Finding at least 12 of the seeded defects is a pass.
3. **Optional script**, from the repo root, needs Python 3.11+ and nothing else:

```bash
# See what "broken" looks like (it should fail)
python3 stacks/pm-prd-markdown/examples/budget-alerts/scripts/check_prd.py exercises/pm/02-fix-the-flawed-prd/inputs

# Your fixed workspace (must pass)
python3 stacks/pm-prd-markdown/examples/budget-alerts/scripts/check_prd.py workspaces/pm --strict
```

The script only checks structure: headings, story line format, Given/When/Then words, epic and goal links, the story index. A pass does not mean the PRD is good.

## Done when

- [ ] `docs/defects-expense-fast-track.md` lists every defect you found with file, line, rule and fix, and who found it
- [ ] No story is bigger than one sprint. The old receipt mega-story is split into separate stories
- [ ] No story is written as a database or code task
- [ ] Every AC is Given/When/Then and every Then can be checked by a tester in one step
- [ ] Every goal and success metric has a baseline, a target and a window
- [ ] Receipt and approval rules match `expense_policy.json` exactly
- [ ] Non-goals exist and hold the work you cut, each with a reason
- [ ] Every story traces to an epic in the Epics table and is linked in the User Stories index
- [ ] The NFR section covers Performance, Security, Privacy, Accessibility, Internationalization and Observability, each with a number or named standard
- [ ] Edge Cases lists at least 5 real scenarios, each mapped to a story
- [ ] `/pm-validate` says "Ready to decompose? Yes" and `docs/tickets-*.md` exists

## Stretch

- **Find the checker's blind spot.** Run the script with `--strict` on the broken inputs. One NFR says only "the app should be fast". Why does strict mode not flag it? Read `check_prd.py` and explain in one sentence.
- **Trace the evidence.** For every claim in the Problem section, add the ticket IDs or interview participant that back it. Delete any claim you cannot back.
- **Policy as a glossary.** Add glossary entries for "receipt threshold" and "approval limit" that quote `expense_policy.json` with the cents value, so the next PM cannot get them wrong.
