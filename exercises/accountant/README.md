# Accountant Exercises: Northwind Co. October 2026 Close

Three exercises from one month-end close. You are on the Northwind Co. close team. October 2026 closes on 2026-11-05. Your controller has opened three tickets: the bank rec, the flux review, and JE testing with the close memo.

You do not need to program. Cursor's agent reads the files, matches the lines and does the arithmetic. You tell it what to build, then you review the result in Excel or Google Sheets the way you would review a staff accountant's work: check the tie-out, follow a few numbers to their source, and ask questions.

All data is synthetic. Northwind Co., its people and its vendors are invented.

## The exercises

| # | Ticket | Time | You produce | Checked against |
|---|---|---|---|---|
| 1 | [October bank rec](01-october-bank-rec/README.md) | 45 to 60 min | Bank rec working paper for GL 1010 with a 0.00 difference, plus proposed entries | `01-october-bank-rec/checks/expected.csv` (9 reconciling items, balances, 4 proposed entries) |
| 2 | [Flux analysis](02-flux-analysis/README.md) | 45 to 60 min | Flux working paper, October actual vs budget and vs September, every flagged account explained or sent to its owner | `02-flux-analysis/checks/expected.csv` (22 accounts, class and explanation status) |
| 3 | [JE testing and close memo](03-je-testing-close-memo/README.md) | 60 to 75 min | JE testing exceptions list, the 2150 accrual tie-out, and the October close memo | `03-je-testing-close-memo/checks/expected.csv` (24 exceptions across 9 tests, population, accrual) |

Total: about 2.5 to 3.5 hours. Exercise 3 reuses the results of 1 and 2 in the memo, so do them in order.

## Works with either stack

| Stack | You work in | Proof it ties |
|---|---|---|
| `sheets-accounting` (default) | CSV or XLSX working papers in `workspaces/accountant/working/` | `TIE-OUT` rows at 0.00, `tie-out-checker` agent |
| `python-accounting` (scripted) | Python steps in `src/`, reports in `output/` | pytest tie-out tests |

The tickets, inputs and expected answers are the same for both. The READMEs give the sheets file names. With `python-accounting`, the same command writes to `output/` instead.

## Flow

```
/set-persona add accountant
/setup-stack accountant                 # Enter for sheets-accounting
/architect accountant exercises/accountant/01-october-bank-rec/README.md
/start-session accountant
  /acct-reconcile 1010 2026-10          # exercise 1
  /acct-variance 2026-10                # exercise 2
  /acct-je-test 2026-10                 # exercise 3
  /acct-close-handoff 2026-10           # exercise 3
/next-session
```

## Setup for every exercise

Copy the Northwind files you need into your workspace once:

```
Ask the agent: "Copy the files listed in exercises/accountant/01-october-bank-rec/README.md
from exercises/_data/northwind/ into workspaces/accountant/data/raw/. Do not change them."
```

Source files stay read-only. Row numbers in every citation count the header as row 1, so the first data row is row 2.

Put this in `workspaces/accountant/docs/close-plan.md` before you start (the commands stop and ask if it is missing):

| Setting | Value |
|---|---|
| Entity | Northwind Co. (NW-US and NW-CA, reported in USD) |
| Period | 2026-10-01 to 2026-10-31, close date 2026-11-05 |
| Overall materiality | $25,000.00 |
| Flux threshold | more than $10,000.00 AND more than 10%, vs budget and vs September |
| Accounts in scope | 1010 Operating Cash, 2150 Accrued Reimbursements, expense accounts 6000 to 6800 |

## How it is checked

Each exercise has a `checks/expected.csv` with the key figures: reconciling items, flagged accounts, exceptions and their amounts. Compare your working paper to it by eye. The key is hidden from the agent by `.cursorignore`, so open it yourself. See [checks/compare.md](checks/compare.md). No script is needed.

A result passes when every row in `expected.csv` is on your paper with the same id and amount, and your paper has no extra exceptions the key does not list (or you can explain each one).

## For instructors

Each exercise has a `SOLUTION.md` with the exact expected numbers, the traps, and grading notes. Every figure was recomputed from the CSVs in `exercises/_data/northwind/`. The full answer key for the dataset is `exercises/_data/README.md` (sections C to F). Do not hand `SOLUTION.md` to students before they finish.

Note: `exercises/_data/README.md` stays visible to the agent because the data-scientist track reads its column reference. Only `answer_key.json`, `SOLUTION.md` and the `checks/expected*` files are hidden by `.cursorignore`.
