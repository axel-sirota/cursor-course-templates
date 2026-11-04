# Vibe: Spreadsheet Close Workbook

## What we are building

A close workbook is a set of working papers a reviewer can tick. In this stack each working paper is a CSV (or XLSX) file the agent writes in `working/`, and the close memo is a markdown file in `output/`. You never write code. You tell the agent which paper to build, you open it in Excel or Google Sheets, and you check the tie-out rows.

Why let the agent build the paper:
- **Matching 1,400 bank lines by hand takes a day.** The agent does it in minutes and lists every line it could not match.
- **Every number keeps its address.** Each row cites the source file and row, so you can check any amount in under a minute.
- **The tie-out rows are your tick marks.** If one is not 0.00, the paper is not done, no matter how good it looks.

## The flow

```
data/raw/ ──► Sources list ──► Working paper ──► TIE-OUT rows ──► Close memo
(read-only)   rows and          BANK / BOOK,       every check      output/close-memo-
              control totals    flux lines,        = 0.00           <period>.md
                                JE exceptions
```

| Step | You do | The agent does | Fails when |
|---|---|---|---|
| Sources | Copy extracts into `data/raw/` | Counts rows, totals amounts, writes `working/sources-<period>.csv` | a file is missing or a total does not agree with its balance |
| Working paper | Name the command and the template | Matches, classifies, writes rows with file and row | (never fails; it lists what it could not match) |
| Tie-out | Open the paper, filter `TIE-OUT` | Fills expected, actual, difference | any difference is not 0.00 |
| Memo | Review and sign | Drafts the memo from the papers | a memo number has no working paper behind it |

## Rules that shape the papers

1. **Raw is sacred.** Never sort, filter-and-save or retype a source file. The hook warns if anything edits `data/raw/`.
2. **Every row has an address.** `source_file` + `source_row`, or a formula over cited rows.
3. **No plugs.** An amount you cannot explain is an `UNRECONCILED` row, not a quiet adjustment.
4. **Classify, do not net.** Each unmatched item is its own row with a category.
5. **Propose, do not post.** Adjusting entries are rows marked `PROPOSED - NOT POSTED`. A person books them in the ERP.
6. **Check the paper, not the chat.** A number in a chat reply is a claim. A number on a paper with a source row is evidence.

## Where Excel and Sheets fit

- **Review**: open any CSV in `working/` directly. Use filters on `section` and `status`.
- **Edit**: do not edit a working paper by hand. Tell the agent what to change, so the citation stays with the number. If you must add a note, add it in a new column at the right.
- **Save**: the agent reads saved files only. Save before you ask it a question about a file you have open.
- **XLSX**: ask for one when a reviewer wants live formulas. The CSV stays the record.

## When this stack fits

**Use sheets-accounting when:**
- You review in Excel or Sheets and do not want to read code
- The close is a few accounts and a few thousand lines
- You want the agent to do the heavy lifting and you want to check its work line by line

**Use python-accounting when:**
- The same papers run every month and you want a rerun in seconds
- Someone on the team can read short Python and pytest
- You want automated tests instead of tie-out rows checked by eye

## Reference

`examples/bank-rec-toy/` is a complete bank rec working paper and close memo on a 9-line toy dataset. Read it once before your first paper.
