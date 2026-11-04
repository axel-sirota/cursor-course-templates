# Exercise 1: October Bank Rec (GL 1010)

**Time:** 45 to 60 minutes
**You produce:** `workspaces/accountant/working/recon-1010-2026-10.csv` with a difference of 0.00, every reconciling item on its own row, and proposed entries for the book-side items.

## Ticket

> **CLOSE-1042** · Assignee: Staff Accountant · Due: BD+2 (2026-11-03)
>
> Reconcile 1010 Operating Cash (NW-US) to the October bank statement. GL and bank do not agree at 10/31 and the gap is about $25.8K. September reconciled with no open items, so every difference is October activity. List each reconciling item, propose entries for anything the GL is missing or has wrong, and get the difference to zero. No plugs.
>
> Treasury says two checks cut in the middle of the month cleared late. Check them, but they may not be reconciling items.

## Inputs

Copy these from `exercises/_data/northwind/` into `workspaces/accountant/data/raw/`:

| File | What it is |
|---|---|
| `bank_statement_2026-10.csv` | 1,429 bank lines for October. `amount_cents` is signed (deposits positive). `reference` matches a token in the GL description |
| `gl_journal.csv` | Every GL line for September and October. Use account `1010`, entity `NW-US`, period `2026-10` |
| `gl_balance_1010_2026-10.csv` | GL and bank opening and closing balances |
| `gl_accounts.csv` | Chart of accounts, for the proposed entries |
| `payouts_2026-10.csv` | Reimbursement payout file. Tells you what was actually paid when the GL and bank disagree |

Amounts are in cents. Divide by 100 once, on the paper.

## Task

1. **Sources.** List each input with its row count and control total in `working/sources-2026-10.csv`. Confirm opening + October activity = closing for both the bank and GL 1010.
2. **Match.** One-to-one on reference + amount. A GL line and a bank line with the same reference but a different amount are not a match. Flag them.
3. **List every unmatched line** on both sides with its file and row. Classify each: deposit in transit, outstanding check, bank item not booked, GL duplicate, keying error.
4. **Reconcile.** Adjusted bank (bank closing + deposits in transit - outstanding checks) must equal adjusted book (GL closing +/- book-side items). Difference 0.00.
5. **Propose entries** for the book-side items. Debits = credits. Each one `PROPOSED - NOT POSTED`.
6. **Tie out.** Fill the `TIE-OUT` rows from the template.

## Commands and agents

```
/acct-reconcile 1010 2026-10
```

Then tell the agent which template and file to use:

```
Write the result to working/recon-1010-2026-10.csv using templates/recon-workpaper-template.csv.
Cite source_file and source_row on every amount. No plugs.
```

| When | Use |
|---|---|
| Paper written | `tie-out-checker` agent on `working/recon-1010-2026-10.csv` |
| Two lines with the same reference disagree | Ask: "Which file shows what was actually paid?" |
| Before you share the paper | `pii-redactor` agent (bank text includes employee ids) |

With `python-accounting`: `/acct-reconcile` writes `output/recon-1010-2026-10.md`, `output/proposed_je_2026-10.csv` and `tests/test_recon_1010.py`.

## Done when

- [ ] Difference is 0.00 (adjusted bank = adjusted book)
- [ ] Every reconciling item is its own row with file and row. None netted
- [ ] Each item is classified, and bank-side vs book-side is right
- [ ] The two late-clearing checks are not on the rec, and you can say why
- [ ] Proposed entries cover the bank fee, the interest, the duplicate and the keying error. Each balances
- [ ] Every `TIE-OUT` row is 0.00 or 0
- [ ] `tie-out-checker` passes
- [ ] Your paper agrees with `checks/expected.csv` (see `../checks/compare.md`)
- [ ] Nothing in `data/raw/` changed

## Stretch

- **Who was overpaid?** The duplicate GL line is a duplicate posting, not a second payment. Use the bank file and `payouts_2026-10.csv` to prove the employee was paid once.
- **Accrual effect.** Both GL errors hit 2150 Accrued Reimbursements as well as cash. Say by how much 2150 is understated. You will need this in exercise 3.
- **XLSX.** Ask for an `.xlsx` copy with live `=SUM()` formulas in the adjusted balance rows. Open it, change nothing, and confirm Excel shows the same totals.
