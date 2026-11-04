# Accountant Persona Pack

For corporate accountants who run month-end close: bank reconciliations, flux analysis, journal entry testing and the close memo. Every number in a report ties to a source file and row, and pytest proves it. Installed with `/set-persona accountant`. Synthetic Northwind Co. data only.

## What this pack adds

**Commands:**
- `/acct-reconcile`: match bank lines to GL lines, list every unmatched item, prove the difference is 0.00
- `/acct-variance`: budget vs actual and month over month flux, flagged against your materiality threshold
- `/acct-je-test`: test journal entries for duplicates, weekend and after-hours postings, round amounts, self-approval and approval limits
- `/acct-close-handoff`: write the close memo with tie-out evidence and open items, sign-off left blank

**Subagents:**
- `tie-out-checker`: every number cites a file and row, totals tie, debits = credits, nothing unmatched is dropped
- `controls-checker`: SOX JE review (segregation of duties, approval limits, posting window, round amounts, duplicates) mapped to control references
- `pii-redactor`: replaces names, emails, tax IDs and full account numbers with IDs or masks

**Hooks:**
- `afterFileEdit`: `protect-raw.sh` prints a loud warning when anything under `data/raw/` is edited
- `stop`: `tie-out-check.sh` runs `pytest -q tests/` when `output/` has files (non-blocking)

**MCP servers:**
- `accountant-data` (filesystem server): scoped to `workspaces/accountant/data`. **No credentials required.**

**Rule:**
- `000-accountant-workflow.mdc`: raw data read-only, outputs to `output/`, no hardcoded amounts, cite sources, show formulas, no personal data, materiality in the plan

## How this pack pairs with `setup-stack`

Run `/setup-stack accountant` next. It offers two stacks with the same Close Workbook shape:

- `sheets-accounting` (default, no code): the agent writes CSV / XLSX working papers in `working/` and you review them in Excel or Google Sheets. Rules: every number cites a file and row or a formula, no plugs, a `TIE-OUT` section at the bottom of each paper. Templates: starter, phase checklist, recon and flux working papers, close memo. Example: `examples/bank-rec-toy/`.
- `python-accounting` (scripted): Close Workbook rules (integer cents, explicit dtypes, tie-out tests), templates (recon, close memo, phase checklist) and the `examples/bank-rec/` reference reconciliation.

The exercises in `exercises/accountant/` work with either one.

## No external systems

No ERP, bank or accounting-system connection. Sources are CSV or XLSX extracts you place in `data/raw/`. Nothing is posted anywhere; proposed entries stay in `output/` for a person to book.

## Prerequisites

See `SETUP.md` for Python, the virtual environment and the smoke test.
