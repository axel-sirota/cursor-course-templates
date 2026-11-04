# Close plan: Tidewater Tools Co., period 2026-03

Entity: Tidewater Tools Co. (toy data)
Period: 2026-03-01 to 2026-03-31
Overall materiality: $500.00
Flux threshold: not in scope for this example
Accounts in scope: 1010 Operating Cash

## Sources
| File | Rows | Control total | Ties to |
|---|---:|---:|---|
| data/raw/bank_statement_2026-03.csv | 9 | 374.47 | bank opening 12,500.00 to closing 12,874.47 (balances rows 4 and 5) |
| data/raw/gl_1010_2026-03.csv | 9 | 2,137.85 | GL opening 12,500.00 to closing 14,637.85 (balances rows 2 and 3) |
| data/raw/balances_2026-03.csv | 4 | | |
| data/raw/gl_accounts.csv | 4 | | |

## Working papers
| Paper | Command | File | Template |
|---|---|---|---|
| Bank rec 1010 | /acct-reconcile 1010 2026-03 | working/recon-1010-2026-03.csv | templates/recon-workpaper-template.csv |
| Close memo | /acct-close-handoff 2026-03 | output/close-memo-2026-03.md | templates/close-memo-template.md |
