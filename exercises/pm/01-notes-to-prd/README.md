# Exercise 1: Notes to PRD

**Time:** 75 to 90 minutes
**Needs:** `/set-persona add pm` and `/setup-stack pm` done
**You produce:** `prds/receipt-approval-speed.md`, one file per story in `stories/`, entries in `glossary.md`, and `docs/validation-receipt-approval-speed.md` from `/pm-validate`.

## Scenario

You are the PM for Northwind Expense, the internal expense app of the fictional Northwind Co. Research handed you six interview write-ups and a sample of last month's support tickets. Leadership wants one PRD for the next quarter that attacks the two biggest pain areas.

Your first job is to find out which two areas those are, from the data, not from opinion. The brief says "receipt capture and approval speed". Check that the tickets agree before you write a word.

## Inputs

| File | What it is |
|---|---|
| `../../_data/northwind/interview_notes.md` | six short user interviews, P1 to P6 |
| `../../_data/northwind/support_tickets.csv` | 60 October tickets (a 1-in-11 sample). Columns: `ticket_id`, `created_at`, `category`, `text` |
| `../../_data/northwind/usage_metrics.csv` | monthly users and tickets per feature area, for baselines |
| `../../_data/northwind/expense_policy.json` | the expense policy. Amounts in cents (`7500` = $75.00) |
| `inputs/product-brief.md` | five-line product summary for `plans/interface-contract.md` |

These files are already generated. Do not run any generator.

## Setup

```bash
mkdir -p workspaces/pm/research
cp exercises/_data/northwind/interview_notes.md \
   exercises/_data/northwind/support_tickets.csv \
   exercises/_data/northwind/usage_metrics.csv \
   exercises/_data/northwind/expense_policy.json \
   workspaces/pm/research/
```

## Task

1. **Size the pain (15 minutes).** Ask Cursor to count `support_tickets.csv` by `category`, then group the tickets inside the top two categories by what the user is complaining about. Save the result as `research/2026-10-ticket-themes.md`: a table of theme, ticket count and ticket IDs. Check one count by hand.
2. **Plan.** Run `/architect pm exercises/pm/01-notes-to-prd/README.md`. Put the five lines from `inputs/product-brief.md` at the top of `plans/interface-contract.md`.
3. **Draft the PRD.** Run `/start-session pm`. Fill `prds/receipt-approval-speed.md` from the template:
   - **Problem:** who hurts, how often, what it costs. Every claim cites a ticket count, ticket IDs or an interview participant.
   - **Goals:** 2 or 3, each with a baseline, a target and a time window.
   - **Non-goals:** at least 3, each with a reason. The other pain areas (mobile, currency, policy) are good candidates.
   - **Epics:** exactly 3. Every epic points at a goal.
   - **Stories:** at least 2 per epic, one file each in `stories/`, INVEST, Given/When/Then AC with real values.
   - **NFRs:** all six categories, each with a number or a named standard.
   - **Edge Cases:** at least 5, each mapped to a story.
4. **Validate.** Run `/pm-validate prds/receipt-approval-speed.md`. Fix every Critical finding. Re-run until the verdict is "Ready to decompose? Yes".
5. **Decompose and report.** Run `/pm-decompose prds/receipt-approval-speed.md`, set two tickets to `In Progress` by hand, then run `/pm-report`.
6. **Hand off.** Run `/next-session`. Record validated and open story counts.

## Commands to use

```
/set-persona add pm
/setup-stack pm                                        # pm-prd-markdown
/architect pm exercises/pm/01-notes-to-prd/README.md   # this README is the plan source
/start-session pm
/pm-validate prds/receipt-approval-speed.md            # docs/validation-receipt-approval-speed.md
/pm-decompose prds/receipt-approval-speed.md           # docs/tickets-<epic>.md
/pm-report                                             # docs/status-<date>-<epic>.md
/next-session
```

Work only inside `workspaces/pm/`. The PM rules and the INVEST and Given/When/Then hooks only fire there.

## How it is checked

1. **`/pm-validate`** says "Ready to decompose? Yes" with no Critical findings left.
2. **Instructor key.** Your ticket counts and themes are compared with the key. The PRD must cite the themes listed there.
3. **Optional script**, from the repo root, needs Python 3.11+ only:

```bash
python3 stacks/pm-prd-markdown/examples/budget-alerts/scripts/check_prd.py workspaces/pm --strict
```

Use `stacks/pm-prd-markdown/examples/budget-alerts/` as the quality bar. Your PRD should read like that one.

## Done when

- [ ] `research/2026-10-ticket-themes.md` shows the category counts and the themes inside receipts and approvals, with ticket IDs
- [ ] The Problem section cites ticket counts and at least 3 interview participants
- [ ] Every goal has a baseline, a target and a time window
- [ ] 3 epics, each with at least 2 stories in `stories/`, each story linked in the User Stories index
- [ ] Every story is "As a <named user>, I want ... so that ..." and has Given/When/Then AC with real values
- [ ] Every receipt or approval number matches `expense_policy.json`
- [ ] All six NFR categories present with a number or named standard
- [ ] At least 5 edge cases, each mapped to a story
- [ ] `/pm-validate` verdict is Yes, and `docs/tickets-*.md` and `docs/status-*.md` exist

## Stretch

- **Anecdote vs data.** Two tickets say a claim waited 21 and 27 days for approval. Ask Cursor to compute the real submit-to-approve time from `exercises/_data/northwind/expense_claims.csv` (`submitted_at`, `approved_at`). Is the median close to those tickets? Which number belongs in the baseline, and what does the gap tell you about the goal?
- **Duplicate submissions.** P4 says AP sees duplicate claims every week. `expense_lines.csv` has 90 exact duplicate lines across claims and 45 near-duplicates (1 cent or 1 day apart). Should duplicate detection be a fourth epic or a Non-goal? Write the decision record in `decisions/`.
- **One diagram.** Add a single Mermaid flowchart from goals to epics to stories, like the budget-alerts example.
