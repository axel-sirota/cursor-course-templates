# Exercise 3: JE Testing and the October Close Memo

**Time:** 60 to 75 minutes
**You produce:**
- `workspaces/accountant/working/je-test-2026-10.csv`: every journal entry exception, one row per entry per test, with source row and policy reference
- `workspaces/accountant/working/accrual-2150-2026-10.csv`: the 2150 Accrued Reimbursements tie-out
- `workspaces/accountant/output/close-memo-2026-10.md`: the October close memo

## Ticket

> **CLOSE-1051** · Assignee: Senior Accountant · Reviewer: Controller · Due: BD+4 (2026-11-05)
>
> Two things before we sign off October.
>
> 1. **JE testing for the SOX file.** Run the journal entry tests over the full GL extract (September and October, pulled 2026-11-12). Use the fraud risk characteristics from AS 2401 (unusual or seldom-used accounts, entries by people who do not normally post, entries at period end or after close, intercompany entries without a matching side) and our usual analytics (weekend and holiday postings, round amounts, entries just under the $10,000 approval limit, self-approval, duplicates). Policy is in `je_policy.json`.
> 2. **Close memo.** Pull together the bank rec (exercise 1), the flux (exercise 2), the JE testing and the 2150 accrual tie-out. Approved-but-unpaid claims should equal the 2150 balance. They do not. Explain the gap.

## Inputs

Copy these from `exercises/_data/northwind/` into `workspaces/accountant/data/raw/`:

| File | What it is |
|---|---|
| `gl_journal.csv` | 13,014 GL lines, 5,274 entries, Sep and Oct 2026. `entry_date` is when it was keyed, `posting_date` is the accounting date |
| `je_policy.json` | Close dates, company holidays, manual JE approval limit, preparer rule, intercompany rule |
| `employees.csv` | Departments and titles. Finance titles are the people who normally post. Use ids, not names, on your paper |
| `gl_accounts.csv` | Chart of accounts, to spot accounts with little or no activity |
| `expense_claims.csv` | Claim headers. Status `approved` = approved, not yet paid |
| `expense_lines.csv` | Claim lines. USD value = `amount_cents x fx_rate` of the claim, rounded half up to the cent |
| `gl_opening_balances_2026-09-01.csv` | Opening balances, including 2150 |

Plus your results from exercises 1 and 2: `working/recon-1010-2026-10.csv` and `working/flux-2026-10.csv`.

## Task

**Part A: JE testing**

1. **Population.** Count entries and lines, total debits and credits. Confirm every entry balances. Write the counts as `POPULATION` and `TIE-OUT` rows.
2. **Run every test** below. Write one `EXCEPTION` row per entry per test, with `je_id`, test, the first GL row of the entry, and the policy it breaks.

| Test | Rule to apply | Basis |
|---|---|---|
| Weekend or holiday posting | `posting_date` is Saturday, Sunday or a company holiday in `je_policy.json` | common analytic |
| Preparer outside Finance | `preparer_id` is not a Finance employee and not a service account (`SVC-*`) | AS 2401: people who do not normally post |
| Entered after close | `entry_date` after the period's `close_date` | AS 2401: post-closing entries |
| Round amount | MANUAL entry with a line that is a whole multiple of $1,000.00 | common analytic |
| Just under the limit | MANUAL entry with total debits from $9,500.00 to $9,999.99 | common analytic |
| Seldom-used account | Entry touches an account used by only 1 or 2 entries in the two months | AS 2401: unusual or seldom-used accounts |
| Self-approved | `preparer_id` equals `approver_id` | policy: preparer and approver must differ |
| Duplicate | Same entity, posting date, description and identical lines on two `je_id`s. Report the second | common analytic |
| Intercompany without offset | IC reference (`IC-YYMM-NN`) in NW-US with no NW-CA entry for the same reference | policy: intercompany rule |

3. **Controls review.** Run the `controls-checker` agent on the paper. Record its findings.

**Part B: 2150 accrual tie-out**

4. **Expected accrual.** Sum the USD value of every claim with status `approved` at 2026-10-31.
5. **GL balance.** 2150 opening at 2026-09-01 plus all September and October 2150 activity. 2150 is a credit-balance account.
6. **Explain the gap** between expected and GL. Use your exercise 1 results. The unexplained remainder must be 0.00.

**Part C: Close memo**

7. **Write the memo** from `templates/close-memo-template.md`. Every number names its working paper. Proposed entries from exercise 1 go in the proposed entries section. Open items get an owner role and a due date. Sign-off stays blank.

## Commands and agents

```
/acct-je-test 2026-10
/acct-close-handoff 2026-10
```

Then:

```
Write the JE testing to working/je-test-2026-10.csv using the JE testing columns in
templates/accounting-starter.md. Test the full extract (2026-09 and 2026-10). Run every test in the
exercise README, including ones that find nothing. Use employee ids, not names.
```

| When | Use |
|---|---|
| JE paper written | `controls-checker` agent, then `pii-redactor` agent |
| Accrual paper written | `tie-out-checker` agent on `working/accrual-2150-2026-10.csv` |
| Memo drafted | `tie-out-checker` agent on `output/close-memo-2026-10.md` |
| An exception looks fine | Ask: "What evidence would clear this? Who would I ask?" Leave it `OPEN` until you have it |

With `python-accounting`: `/acct-je-test` writes `output/je-test-2026-10.md`, an exceptions CSV and `tests/test_je_test.py`.

## Done when

- [ ] Population ties: entries, lines, total debits = total credits
- [ ] All 9 tests ran; every exception is on the paper with `je_id`, test and source row
- [ ] Exceptions agree with `checks/expected.csv`. Any extra row has a reason
- [ ] `controls-checker` run and findings recorded
- [ ] No employee names on the paper (`pii-redactor` run)
- [ ] Accrual tie-out shows expected, GL, gap, the two items that explain it, and 0.00 unexplained
- [ ] Memo covers the bank rec, flux, JE testing and accrual, every number cites a paper
- [ ] Open items have owner roles and due dates; sign-off blank
- [ ] Nothing in `data/raw/` changed

## Stretch

- **Intercompany.** Compute NW-US 1310 and NW-CA 2310 at 2026-10-31. Do they agree? By how much, and which entry explains it?
- **Late entries and the flux.** Three entries were keyed after the October close. Do any of them change your flux paper from exercise 2?
- **Approval limit.** Are there MANUAL entries of $10,000.00 or more that were not approved by the Controller?
