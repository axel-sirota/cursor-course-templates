# Exercise 2: October Flux Analysis

**Time:** 45 to 60 minutes
**You produce:** `workspaces/accountant/working/flux-2026-10.csv` with every budgeted expense account, October actual vs October budget and vs September actual, each account classed against the threshold, and every flagged account explained from a source or sent to its owner.

## Ticket

> **CLOSE-1047** · Assignee: Senior Accountant · Due: BD+3 (2026-11-04)
>
> FP&A needs the October expense flux for the CFO pack. Compare October actual to October budget and to September actual, by account. Threshold is more than $10,000 AND more than 10%. Explain anything over both using the department notes. If a note does not cover it, do not guess: mark it "owner to explain" and name the owner. Accounts over only one threshold get a short note, no explanation needed.

## Inputs

Copy these from `exercises/_data/northwind/` into `workspaces/accountant/data/raw/`:

| File | What it is |
|---|---|
| `gl_journal.csv` | GL lines for September and October. Actual = sum of `debit_cents - credit_cents` for the account and period |
| `budget_2026.csv` | Monthly budget by cost center and account, Aug to Dec 2026. Use month `2026-10` |
| `gl_accounts.csv` | Account names |
| `context_notes_2026-10.md` | Department head notes for the October review. Not checked against the ledger |

Level: account. Sum all cost centers and both entities. Use the 22 accounts in the budget file (6000 to 6800). Accounts with activity but no budget (6950, 6990, revenue, balance sheet) are outside this paper.

## Task

1. **Build the paper** from `templates/flux-template.csv` (python-accounting has no flux template: copy `stacks/sheets-accounting/templates/flux-template.csv` into `workspaces/accountant/templates/` first): budget, September actual, October actual, both variances in $ and %.
2. **Class each account** for each comparison: `both` (over $10,000 and over 10%), `pct_only`, `dollar_only`, or `under`.
3. **Explain** every `both` account from `context_notes_2026-10.md`. Cite the note section. Check the note's amount against the variance.
4. **Owner to explain.** A `both` account with no matching note gets `OWNER TO EXPLAIN` and the owner role.
5. **Note the near misses.** Accounts that are `pct_only` or `dollar_only` get a one-line note saying which threshold they miss. No explanation needed.
6. **Tie out.** Budget, September and October columns each tie to their source totals.

## Commands and agents

```
/acct-variance 2026-10
```

Then:

```
Write the result to working/flux-2026-10.csv using templates/flux-template.csv.
Threshold: more than $10,000.00 AND more than 10%. Explanations must cite context_notes_2026-10.md
by section, or read OWNER TO EXPLAIN. Do not invent explanations.
```

| When | Use |
|---|---|
| Paper written | `tie-out-checker` agent on `working/flux-2026-10.csv` |
| A note gives an amount | Ask: "Does the note amount agree with the variance? By how much?" |
| An account is flagged with no note | Ask: "Which department owns this account? Draft the question for them." |

With `python-accounting`: `/acct-variance` writes `output/flux-2026-10.md` and `tests/test_flux.py`.

## Done when

- [ ] 22 accounts on the paper, each with budget, September, October and both variances
- [ ] Classes agree with `checks/expected.csv` for both comparisons
- [ ] Each `both` account is explained with a note section cited, or reads `OWNER TO EXPLAIN` with an owner
- [ ] No explanation the notes do not support
- [ ] `pct_only` and `dollar_only` accounts have a note naming the threshold they miss
- [ ] Notes that match no variance are called out as such
- [ ] Every `TIE-OUT` row is 0.00
- [ ] `tie-out-checker` passes
- [ ] Nothing in `data/raw/` changed

## Stretch

- **Cost center drill-down.** For each `both` account, which cost center drives the variance? Does it match the department that wrote the note?
- **November preview.** Two notes say spend moved from November into October. Check the November budget for those accounts and say what November flux to expect.
- **6150 Office Supplies** is over 10% but under $10,000. Ask the agent to find the single expense line that drives most of it.
