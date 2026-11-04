# Example: toy bank reconciliation (spreadsheet stack)

A complete working paper and close memo for a 9-line toy dataset (Tidewater Tools Co., March 2026). It shows the shape every paper in this stack follows. It is not the Northwind exercise and its numbers are not the exercise answers.

## Files

| File | What it is |
|---|---|
| `data/raw/bank_statement_2026-03.csv` | 9 bank lines, amounts in cents, running balance |
| `data/raw/gl_1010_2026-03.csv` | 9 GL lines for 1010, debit and credit in cents |
| `data/raw/balances_2026-03.csv` | Opening and closing balances, GL and bank |
| `data/raw/gl_accounts.csv` | 4-account chart for the proposed entries |
| `docs/close-plan.md` | Period, materiality, sources with control totals |
| `working/recon-1010-2026-03.csv` | The working paper: HEADER, SOURCE, MATCHED, BANK, BOOK, PROPOSED-JE, TIE-OUT |
| `output/close-memo-2026-03.md` | The close memo built from the paper |

## What is planted

| Item | Side | Amount | Paper row |
|---|---|---:|---|
| Deposit in transit RCPT-304 | Bank | 2,050.00 | B2 |
| Outstanding check CHK 1003 | Bank | -315.00 | B3 |
| Bank fee not booked | Book | -15.00 | K2 |
| Interest not booked | Book | 4.62 | K3 |
| Vendor payment keyed 1,257.40, cleared 1,275.40 | Book | -18.00 | K4 |

Adjusted bank 14,609.47 = adjusted book 14,609.47. Difference 0.00.

## How to read it (5 minutes)

1. Open `working/recon-1010-2026-03.csv` in Excel or Google Sheets. Turn on filters.
2. Filter `section = TIE-OUT`. Eight rows, every one 0.00 or 0, status PASS.
3. Pick row K2. It cites `bank_statement_2026-03.csv` row 9. Open the bank file and find the -1500 cent fee on line 9 (header is line 1).
4. Filter `section = PROPOSED-JE`. Debits and credits net to 0.00 (row T8). Every row says `PROPOSED - NOT POSTED`.
5. Open `output/close-memo-2026-03.md`. Each amount names the paper row it came from.

## Try it yourself

Ask the agent: "Rebuild `working/recon-1010-2026-03.csv` from the files in `data/raw/` using `templates/recon-workpaper-template.csv`, then compare it to this one." The `TIE-OUT` rows should match.
