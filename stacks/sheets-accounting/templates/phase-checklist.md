# Phase Checklist (spreadsheet close)

Tick every item before moving to the next phase. Paths are relative to `workspaces/accountant/`.

---

## Phase 0: Skeleton

- [ ] `docs/close-plan.md` states entity, period, accounts in scope, overall materiality and the flux threshold ($ and %)
- [ ] Folders exist: `data/raw/`, `working/`, `output/`, `docs/`
- [ ] One paper per workpaper in `working/`, created from its template, headers filled, `TIE-OUT` rows in place
- [ ] Every paper opens in Excel or Google Sheets with the columns intact

---

## Phase 1: Sources

- [ ] Every source file copied into `data/raw/` once
- [ ] `working/sources-<period>.csv` lists every file with row count and control total
- [ ] Opening balances agree with last period's closing balances (cited by file and row)
- [ ] Nothing in `data/raw/` was edited, sorted or re-saved

---

## Phase 2: Reconciliations

- [ ] Matching is one-to-one on reference + amount; second-pass matches flagged, not cleared
- [ ] Every unmatched line on both sides listed with category, amount, file and row
- [ ] No plugs; any unexplained amount is an `UNRECONCILED` row
- [ ] Proposed entries balance and say `PROPOSED - NOT POSTED`
- [ ] Every `TIE-OUT` row is 0.00
- [ ] `tie-out-checker` agent passes on `working/recon-*`

---

## Phase 3: Flux analysis

- [ ] Threshold stated in the paper header and taken from the close plan
- [ ] Budget, prior and actual columns each tie to their source totals (`TIE-OUT` rows)
- [ ] Every account over both thresholds has an explanation with its source, or `OWNER TO EXPLAIN` with an owner role
- [ ] Accounts over only one threshold are classed and noted, not explained
- [ ] No explanation invented by the agent
- [ ] `tie-out-checker` agent passes on `working/flux-*`

---

## Phase 4: JE testing

- [ ] Population ties to the extract (entry count and total debits)
- [ ] Every test in the plan ran, including the ones with zero exceptions
- [ ] Each exception lists `je_id`, test, source row and the policy it breaks
- [ ] `controls-checker` agent run; findings recorded
- [ ] `pii-redactor` agent run on every paper that names people

---

## Phase 5: Close memo

- [ ] `output/close-memo-<period>.md` follows `templates/close-memo-template.md`
- [ ] Every number in the memo names its working paper
- [ ] Accrual tie-outs show expected, GL, gap and what explains the gap
- [ ] Open items have an owner role and a due date
- [ ] Sign-off block left blank
- [ ] `data/raw/` unchanged
