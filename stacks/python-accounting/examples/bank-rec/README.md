# Example: October bank reconciliation (Northwind Co.)

A small, working Close Workbook. It reconciles the Northwind Co. operating cash account (GL 1010) to the October 2026 bank statement. All data is synthetic.

## What is in the data

`scripts/generate_data.py` writes three files to `data/raw/`. It is seeded, so every run produces the same bytes.

| File | Rows | What it is |
|---|---|---|
| `gl_journal_2026-10.csv` | 52 lines, 26 JEs | GL journal lines. Every JE has two lines and balances |
| `bank_statement_2026-10.csv` | 25 lines | Bank statement for the operating account |
| `balances_2026-10.csv` | 2 rows | Opening and closing balance per bank and per GL |

Three exceptions are planted on purpose:

| Exception | Where it shows up | Expected treatment |
|---|---|---|
| Deposit booked 10/31, bank credits it 11/02 | GL only | Deposit in transit. Reconciling item, no entry |
| 35.00 monthly service fee | Bank only | Book it: Dr 6110 Bank Fees / Cr 1010 Cash |
| One vendor payment posted twice | GL has 2 lines, bank has 1 | Reverse the duplicate JE |

## Run it

From this folder:

```bash
python -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt
.venv/bin/python3 scripts/generate_data.py      # optional: data/raw/ ships pre-generated; a rerun writes identical files
.venv/bin/python3 src/reconcile.py              # writes output/
.venv/bin/python3 -m pytest -q                  # tie-out tests
```

On Windows use `.venv\Scripts\python` in place of `.venv/bin/python3`.

## Outputs

| File | Contents |
|---|---|
| `output/bank_rec_2026-10.md` | The reconciliation: adjusted bank vs adjusted book, tie-out table, unmatched items, proposed entries |
| `output/matched_pairs_2026-10.csv` | Each GL line paired with its bank line, both with file and row |
| `output/unmatched_items_2026-10.csv` | Every unmatched item with category, amount, materiality flag, file and row |
| `output/proposed_je_2026-10.csv` | Draft adjusting entries. Status is `PROPOSED - NOT POSTED` |

Expected result: difference 0.00, three unmatched items.

## How the code is laid out

`src/reconcile.py` follows the stack's pipeline. Each step is a plain function:

```
load_gl / load_bank / load_balances    Sources (read data/raw/, record file + row)
validate                               Validate (JEs balance, statement ties, ledger ties)
match_items, classify                  Reconcile (one-to-one on reference + amount)
reconcile                              Tie-out (adjusted bank vs adjusted book)
render_report, write_outputs           Report (output/ only)
```

Money is integer cents end to end. `to_cents` refuses fractions of a cent. Settings such as the materiality threshold sit in one block at the top of the file.

## What the tests prove

| Test | Tie-out point |
|---|---|
| `test_generator_is_seeded` | Same seed, same bytes |
| `test_every_je_balances_debits_equal_credits` | Debits = credits per JE and in total |
| `test_bank_lines_tie_to_statement_closing` | Opening + bank lines = statement closing |
| `test_gl_cash_lines_tie_to_ledger_closing` | Opening + GL cash lines = ledger closing |
| `test_matched_plus_unmatched_equals_source_totals` | Nothing lost or double counted, by count and by cents |
| `test_every_unmatched_source_row_is_listed` | Every unmatched source row appears in the output |
| `test_seeded_exceptions_are_classified` | The three planted items land in the right category |
| `test_reconciliation_difference_is_zero` | Adjusted bank = adjusted book |
| `test_outputs_cite_source_file_and_row` | Every reported item names its file and row |
| `test_raw_files_are_not_modified` | `data/raw/` is read-only |

## Try next

- Change `DUPLICATE_TXN_INDEX` or add a second fee in the generator into a temp folder (`--out-dir`) and watch which tests fail.
- Add a date-window pass to `match_items` for items where the bank reference is missing.
- Run `/acct-reconcile` on this data and compare its output with `output/bank_rec_2026-10.md`.
