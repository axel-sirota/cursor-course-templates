# Spreadsheet Close Starter

Use this to start a close in `workspaces/accountant/`. All paths below are relative to that folder. You do not write code. You tell the agent what to build and you review it in Excel or Google Sheets.

## 1. Folders

```
data/raw/     source extracts, copied once, never touched again
working/      working papers the agent writes (CSV, optional XLSX)
output/       final reports and the close memo
docs/         close plan, materiality, notes
templates/    the templates in this folder
```

Ask the agent: "Create the folders from `templates/accounting-starter.md` and copy the source files I name into `data/raw/`."

## 2. Close plan (write it before any analysis)

Create `docs/close-plan.md`:

```markdown
# Close plan: <entity>, period <YYYY-MM>

Entity: <entity> (synthetic)
Period: <YYYY-MM-01> to <YYYY-MM-DD>
Overall materiality: <amount>
Flux threshold: more than <amount> AND more than <percent>, vs budget and vs prior month
Accounts in scope: <list>

## Working papers
| Paper | Command | File | Template |
|---|---|---|---|
| Sources list | (prompt) | working/sources-<period>.csv | section 3 below |
| Bank rec 1010 | /acct-reconcile | working/recon-1010-<period>.csv | templates/recon-workpaper-template.csv |
| Flux | /acct-variance | working/flux-<period>.csv | templates/flux-template.csv |
| JE testing | /acct-je-test | working/je-test-<period>.csv | section 4 below |
| Close memo | /acct-close-handoff | output/close-memo-<period>.md | templates/close-memo-template.md |
```

## 3. Sources list columns

`working/sources-<period>.csv`:

```
file,rows,control_total,amount_column,ties_to,source_formula
```

One row per file in `data/raw/`. `rows` excludes the header. `control_total` is the sum of the amount column in dollars. `ties_to` names the balance it should agree with (for example `bank closing in gl_balance_1010_2026-10.csv row 6`).

## 4. JE testing columns

`working/je-test-<period>.csv`:

```
section,test,je_id,entity,posting_date,entry_date,source,preparer_id,approver_id,total_debit,accounts,description,source_file,source_row,policy_reference,disposition
```

- `section` is `EXCEPTION` for each finding, `POPULATION` for the counts, `TIE-OUT` for the checks.
- One `EXCEPTION` row per entry per test. `source_row` is the first line of the entry in the GL file.
- `disposition` starts as `OPEN`. The reviewer changes it to `CLEARED` with a reason, or leaves it open for the memo.
- `TIE-OUT` rows: entries on the paper's `POPULATION` row minus entries in the extract = 0; total debits on the paper minus extract total debits = 0.00; total debits minus total credits in the extract = 0.00.

## 5. Skeleton (Phase 0)

Ask the agent: "Create every working paper in the close plan from its template, with the headers filled in, no body rows, and the `TIE-OUT` rows in place." Then open each file in Excel or Sheets and confirm the columns read cleanly.

## 6. Working one paper

1. Run the command (for example `/acct-reconcile 1010 2026-10`) and name the template: "Write the result to `working/recon-1010-2026-10.csv` using `templates/recon-workpaper-template.csv`."
2. Open the paper. Filter `section = TIE-OUT`. Every difference must be 0.00.
3. Pick three amounts and follow `source_file` + `source_row` to the source.
4. Run the `tie-out-checker` agent on the paper.
5. Ask questions in plain language: "Why is JE-003980 on the BOOK side?" The agent answers from the cited rows.

Copy the pattern from `examples/bank-rec-toy/` for every new paper.
