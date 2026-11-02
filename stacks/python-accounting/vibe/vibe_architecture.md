# Vibe: Close Workbook Architecture

## What we are building

A close workbook is a set of workpapers that a reviewer can tick. In this stack each workpaper is a short Python module, a pytest file that proves it ties, and a report in `output/`. Excel is still welcome as a viewer. It is not where the logic lives.

Why code instead of a spreadsheet:
- **Rerun in seconds.** New bank file arrives on day 3? Drop it in `data/raw/`, rerun, done.
- **Every step is visible.** A reviewer reads one function per step instead of hunting for a hidden formula in column AF.
- **Tie-outs are automatic.** The tests are your tick marks. They run every time.

## The pipeline

```
data/raw/ ──► Sources ──► Validate ──► Reconcile / Analyse ──► Tie-out ──► Report ──► output/
 (read-only)   load +      balances,    match, classify,        counts,     markdown,
               file/row    control      flux, JE tests          cents,      CSV, xlsx
                           totals                               difference
```

| Step | Input | Output | Fails when |
|---|---|---|---|
| Sources | files in `data/raw/` | DataFrames with `source_file`, `source_row`, cents columns | a required column is missing, an amount has a fraction of a cent |
| Validate | source DataFrames | list of problems | a JE does not balance, a roll-forward does not tie |
| Reconcile / Analyse | validated DataFrames | matched, unmatched, flux lines, exceptions | (never fails; it classifies) |
| Tie-out | results | pass/fail per check | counts or cents do not add up |
| Report | results | files in `output/` | (never fails; it writes) |

## Rules that shape the code

1. **Raw is sacred.** Code reads `data/raw/` and never writes there. A hook warns if anything edits it.
2. **Every row remembers where it came from.** `source_file` and `source_row` are added at load and survive every merge. That is how a reviewer gets from a number in the memo to a line in the extract.
3. **Integer cents.** Floats lose pennies. Pennies are what reviewers check.
4. **Settings at the top.** Period, accounts, materiality and timing windows are named once. Logic refers to the names.
5. **Classify, do not net.** Every unmatched item is listed with a category. Netting hides errors.
6. **Propose, do not post.** Adjusting entries are written to a CSV marked `PROPOSED - NOT POSTED`. A person books them.

## Where Excel fits

- **Inputs**: `.xlsx` extracts are fine. Read them with `dtype=str` and openpyxl. pandas reads the last saved values, not live formulas.
- **Outputs**: write an `.xlsx` copy of a report when the reviewer wants it (`DataFrame.to_excel`). The markdown and CSV stay the record.
- **Never**: keep logic in Excel formulas that the Python reads back. Pick one place for the logic.

## When this stack fits

**Use python-accounting when:**
- The data arrives as extracts (CSV, XLSX) and fits on a laptop
- The work repeats every month: reconciliations, flux, JE testing, close memos
- A reviewer needs to trace numbers back to source rows

**Use something else when:**
- You need to post to the ERP. That stays in the ERP, with its own approvals
- Data volume needs a warehouse (millions of lines a month). Look at the `python-dbt-snowflake` stack
- The task is a one-off question with no rerun. A spreadsheet may be faster

## Reference implementation

`examples/bank-rec/` is a full workpaper: seeded generator, five-step reconciliation, 17 passing pytest cases. Copy its structure for every new workpaper.
