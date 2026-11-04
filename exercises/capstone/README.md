# Capstone: one feature, several roles

Northwind Co. wants a **receipt fast-track**: claims with every receipt attached and no policy flag skip the manager queue and get paid in the next payout run.

Each role does its part in its own workspace and reads the previous role's output. Nobody edits another role's workspace.

Time: 90 to 120 minutes. Run it as a team (one role per person) or alone with several personas active.

## Setup

```
/set-persona add pm
/set-persona add designer
/set-persona add data-scientist
/set-persona add accountant
/set-persona list
```

Skip the roles nobody in your group plays. Run `/setup-stack <role>` for any role that has no stack yet.

## Steps

| # | Role | Input | Task | Done when |
|---|---|---|---|---|
| 1 | pm | `exercises/_data/northwind/` interview notes, tickets, `expense_policy.json` | `/architect pm @exercises/capstone/README.md`. Write `workspaces/pm/prds/receipt-fast-track.md`: eligibility rule, goals with metrics, 3 to 5 INVEST stories with Given/When/Then | `/pm-validate` says ready |
| 2 | designer | the PRD from step 1 | Add a "Fast-track" status variant to StatusBadge and a fast-track banner to the my-claims screen, tokens only | token and contrast checks pass, one story per new state |
| 3 | data-scientist | the PRD rule + `expense_lines.csv`, `expense_claims.csv` | Count how many October claims would qualify and how many would have qualified while still carrying a seeded duplicate or policy issue | numbers in `workspaces/data-scientist/docs/fast-track-impact.md`, reproducible with a fixed seed |
| 4 | accountant | step 3 numbers + `payouts_2026-10.csv`, GL 2150 | Show the effect on the 2150 Accrued Reimbursements balance if fast-track had run in October, and the control that replaces the skipped manager approval | working paper ties to 0.00, memo names the compensating control |
| 5 | everyone | all of the above | `/read` to see every role's state, then `/next-session` per role | each role has a transition doc |

## Engineers

Engineers stay on the Blog API track (`exercises/engineer/`). If you finish phase 05 early, add a second persona with `/set-persona add <role>` and take one step above.

## Debrief questions

- Which step found a problem in an earlier step's output?
- Did the pm rule survive the data scientist's numbers?
- What does the accountant's compensating control cost the user experience the designer built?
