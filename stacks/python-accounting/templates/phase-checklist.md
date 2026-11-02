# Phase Checklist

Tick every item before moving to the next phase. Paths are relative to `workspaces/accountant/`.

---

## Phase 0: Skeleton

- [ ] `docs/close-plan.md` states entity, period, accounts in scope and materiality threshold
- [ ] Folders exist: `data/raw/`, `data/interim/`, `src/`, `tests/`, `output/`, `docs/`
- [ ] One `src/<workpaper>.py` per workpaper in the plan, with step functions returning empty DataFrames
- [ ] One `tests/test_<workpaper>.py` per workpaper; unbuilt checks marked `xfail(strict=True)`
- [ ] `pytest -q tests/` collects and runs

---

## Phase 1: Sources & validation

- [ ] Every file in `data/raw/` is listed in the plan with row count and control total
- [ ] Loaders read with `dtype=str` and add `source_file` + `source_row`
- [ ] Amounts converted to integer cents; account numbers kept as strings
- [ ] Every JE balances (debits = credits); test passes
- [ ] Opening + activity = closing for each balance file; test passes
- [ ] `git status data/raw/` is clean

---

## Phase 2: Reconciliations

- [ ] Matching is one-to-one on a stated key; second pass (date window) documented if used
- [ ] Matched + unmatched = source, by count and by cents; test passes
- [ ] Every unmatched item listed with category, amount, file and row
- [ ] Difference is 0.00, or equals the listed reconciling items
- [ ] Proposed JEs balance and say `PROPOSED - NOT POSTED`
- [ ] `tie-out-checker` agent passes on `output/recon-*`

---

## Phase 3: Flux analysis

- [ ] Thresholds stated in the report header (amount and %)
- [ ] Current, prior and budget trial balances each tie to their own totals
- [ ] Every line over threshold has an explanation or an `OWNER TO EXPLAIN` flag
- [ ] No explanation invented by the AI; each one names who gave it or the source that supports it
- [ ] `tie-out-checker` agent passes on `output/flux-*`

---

## Phase 4: JE testing

- [ ] Population ties to the JE extract (count and total debits)
- [ ] Tests run: duplicates, weekend and after-hours postings, round amounts, self-approval, over approval limit, unbalanced, missing description
- [ ] Each exception lists JE ID, test name, file and row
- [ ] `controls-checker` agent run; findings recorded
- [ ] `pii-redactor` agent run on every file that names a user

---

## Phase 5: Close memo

- [ ] `output/close-memo-<period>.md` follows `templates/close-memo-template.md`
- [ ] Every number in the memo traces to a workpaper in `output/`
- [ ] Open items have an owner role and a due date
- [ ] Sign-off block left blank for the human preparer and reviewer
- [ ] `pytest -q tests/` passes; `git status data/raw/` is clean
