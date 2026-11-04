# PM Exercises: Northwind Expense

Three exercises that take a product manager from raw research to a validated PRD, a reviewed PRD and a prioritized MVP, all in Cursor. The product is **Northwind Expense**, the internal expense app of the fictional Northwind Co. Employees file claims and attach receipts, managers approve them, Finance AP pays them.

Everything is markdown. Nothing to install. The research inputs (interviews, support tickets, usage metrics, expense policy) are already generated in `exercises/_data/northwind/`. Do not run the generator.

## The exercises

| # | Exercise | Time | You produce | Checked by |
|---|---|---|---|---|
| 1 | [Notes to PRD](01-notes-to-prd/README.md) | 75 to 90 min | ticket theme table, `prds/receipt-approval-speed.md` with 3 epics and story files | `/pm-validate` says Yes + instructor key (ticket counts, themes cited) |
| 2 | [Fix the Flawed PRD](02-fix-the-flawed-prd/README.md) | 60 to 75 min | defect list with file and line, fixed `prds/expense-fast-track.md` and stories | `/pm-validate` says Yes + instructor key (16 seeded defects, 12 to pass) |
| 3 | [RICE and the MVP Cut](03-rice-and-mvp-cut/README.md) | 45 to 60 min | RICE table for 8 features, MVP cut, one-page stakeholder update | instructor key (exact scores and ranking) + peer read |

Total: about 3 to 4 hours. Exercise 1 sets up `workspaces/pm/research/`, which exercises 2 and 3 reuse.

## Data in one table

| File | Used in | What it holds |
|---|---|---|
| `exercises/_data/northwind/interview_notes.md` | 1, 2, 3 | six interviews, P1 to P6: receipts, approvals, mobile, currency, policy |
| `exercises/_data/northwind/support_tickets.csv` | 1, 2 | 60 October tickets (1 in 11 sample) with a category |
| `exercises/_data/northwind/usage_metrics.csv` | 1, 3 | 8 candidate features with monthly users, tickets and minutes to submit |
| `exercises/_data/northwind/expense_policy.json` | 1, 2 | receipt over $75.00, 60-day limit, approval limits. Amounts in cents |

## Flow

```
/set-persona add pm
/setup-stack pm                                        # pm-prd-markdown
/architect pm exercises/pm/01-notes-to-prd/README.md   # the exercise README is the plan source
/start-session pm
  /pm-validate   → docs/validation-<prd>.md   (Three Amigos: dev, QA, gap detector)
  /pm-decompose  → docs/tickets-<epic>.md     (dependency-ordered tickets)
  /pm-report     → docs/status-<date>-<epic>.md
/next-session                                          # transition doc with validated / open story counts
```

All work lives in `workspaces/pm/`. The PM rules and the INVEST and Given/When/Then hooks only fire there. A PRD saved anywhere else gets no checks.

## How work is checked

| Check | What it proves | Needs |
|---|---|---|
| `/pm-validate` | INVEST, testable Given/When/Then AC, NFR coverage, edge cases, gaps. The verdict must be "Ready to decompose? Yes" | Cursor only |
| Instructor key (`SOLUTION.md` in each folder) | the numbers: ticket counts, seeded defects, RICE scores | Instructor |
| `check_prd.py` (optional) | structure only: headings, story format, AC keywords, epic and goal links, story index | Python 3.11+, standard library |

Run the optional script from the repo root:

```bash
python3 stacks/pm-prd-markdown/examples/budget-alerts/scripts/check_prd.py workspaces/pm --strict
```

The script cannot tell a vague goal from a measurable one, or a $50 rule from a $75 rule. Exercise 2 shows exactly where it stops. The quality bar for every PRD is `stacks/pm-prd-markdown/examples/budget-alerts/`.

## For instructors

Each exercise has a `SOLUTION.md` with the expected numbers, traps, sample answers and grading levels. Ticket counts, defect line numbers, checker output and the RICE table were recomputed from the shipped files with a script. Do not hand `SOLUTION.md` to students before they finish.
