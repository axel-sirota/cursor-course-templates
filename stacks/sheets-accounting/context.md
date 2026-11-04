# Project Context: Sheets Accounting (Close Workbook)

## Architecture Shape
Close Workbook (Sources → Working papers → Tie-out → Memo)
No code to write. The deliverable is a set of working papers (CSV or XLSX) in `working/` and a close memo in `output/`. Cursor's agent reads the source extracts, builds the working papers and drafts the memo. The accountant reviews every paper in Excel or Google Sheets and signs off.
Every working paper ends with a tie-out section. A paper is done when every tie-out row shows a difference of 0.00.

## Tech Stack
- **Tool**: Cursor (agent mode) with the accountant persona pack
- **Working papers**: CSV (UTF-8, comma separated) as the record. XLSX (Excel 2016 or later, `.xlsx`) when a reviewer wants formulas and formatting
- **Viewer**: Microsoft Excel (Microsoft 365 or 2019+) or Google Sheets. Either one opens every file in this stack
- **Memos**: Markdown (`.md`), readable in Cursor's preview
- **No Python, no database, no ERP connection.** Sources are CSV or XLSX extracts placed in `data/raw/`
- **Scripted alternative**: the `python-accounting` stack builds the same papers with pandas 2.x and pytest 8.x tie-out tests. Pick it when the close repeats every month and you want reruns in seconds

## Vibe & Style
- **Accountant first**: the agent does the matching and the arithmetic. You review, question and approve
- **Plain columns**: one header row, one fact per row, ISO dates (`2026-10-31`), account numbers as text (`1010`, not `1,010`)
- **Amounts**: dollars with two decimals and a minus sign for credits or withdrawals (`-35.00`). No thousands separators inside a CSV, they break the columns
- **Source on every row**: `source_file` and `source_row` (header row = 1, so the first data row is 2), or a `formula` that a reviewer can redo by hand
- **Tie-out at the bottom**: every working paper ends with rows in section `TIE-OUT`. Each one shows a difference that must be 0.00
- **Short memos**: facts and amounts, no adjectives. Open items have an owner role and a due date

## Key Rules
- `data/raw/` is read-only. Never edit, sort, filter-and-save or rename a source file. Copy it to `working/` if you need to reshape it
- Every number in a working paper cites a source file and row, or shows its formula over cited rows
- No hardcoded plugs. A difference you cannot explain stays on the paper as `UNRECONCILED` with its amount
- Every working paper ends with a tie-out section. A non-zero tie-out row means the paper is not done
- Materiality is stated in the close plan before any analysis (an overall amount and a flux threshold in $ and %)
- The agent proposes adjusting entries marked `PROPOSED - NOT POSTED`. It never posts and never says an entry is booked
- Do not trust arithmetic in a chat reply. Ask the agent to write the number into a working paper with its source, then check the tie-out rows
- No personal data in prompts or papers. Use employee IDs (`E0065`) and roles (`Accounting Manager`)
- Synthetic data only in this course (Northwind Co.)

## Workspace Layout
Paths are relative to the persona workspace (`workspaces/accountant/`).
```
data/raw/      ← read-only copies of the source extracts (bank, GL, budget, policies)
working/       ← working papers the agent writes: recon, flux, JE testing, sources list (CSV or XLSX)
output/        ← final reports and the close memo, ready for the reviewer
docs/          ← close plan, materiality, vibe docs, review notes
templates/     ← installed by /setup-stack: starter, checklist, CSV templates, memo template
plans/         ← /architect session plans and transitions
```
- **Entry point**: none. Each working paper is built by an `/acct-*` command or a prompt that names the template
- **Check**: open the paper, scroll to the `TIE-OUT` rows, confirm every difference is 0.00, then run the `tie-out-checker` agent
- **Example**: `examples/bank-rec-toy/` is a complete bank rec working paper and memo on a small toy dataset

## Working paper contract
| Paper | File | Template | Done when |
|---|---|---|---|
| Sources list | `working/sources-<period>.csv` | columns in `templates/accounting-starter.md` | every file in `data/raw/` listed with row count and control total |
| Bank rec | `working/recon-<account>-<period>.csv` | `templates/recon-workpaper-template.csv` | `TIE-OUT` rows all 0.00, every unmatched item listed |
| Flux | `working/flux-<period>.csv` | `templates/flux-template.csv` | every account over both thresholds has an explanation or `OWNER TO EXPLAIN` |
| JE testing | `working/je-test-<period>.csv` | columns in `templates/accounting-starter.md` | every test ran, every exception lists `je_id` and source row |
| Close memo | `output/close-memo-<period>.md` | `templates/close-memo-template.md` | every number traces to a working paper; sign-off blank |

## Hooks note
The persona's stop hook looks for a `tests/` folder and prints an advisory when there is none. In this stack the `TIE-OUT` rows and the `tie-out-checker` agent are the proof. The advisory is expected and safe to ignore.

## Active Phase
- Current: Phase 0 (Skeleton)
- Phases: 0 Skeleton → 1 Sources → 2 Reconciliations → 3 Flux analysis → 4 JE testing → 5 Close memo
