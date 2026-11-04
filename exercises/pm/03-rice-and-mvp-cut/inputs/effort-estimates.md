# RICE inputs: Northwind Expense, Q1 2027 planning

From the engineering lead and the research lead, 2026-11-02. Use these rules exactly so every team gets comparable scores. The data for Reach and Impact is in `exercises/_data/northwind/usage_metrics.csv`.

## Formula

```
RICE = Reach x Impact x Confidence / Effort
```

Round the final score to one decimal place. Do not round the inputs.

## Reach

Reach = `monthly_active_users` for the feature's row. People who touch that workflow area in a month.

## Impact

Impact measures how much the feature hurts today, per user.

1. Compute **tickets per 1,000 users** = `support_tickets_per_month` / (`monthly_active_users` / 1000).
2. Pick the starting tier from that number:

| Tickets per 1,000 users | Impact |
|---|---|
| 10 or more | 3 (massive) |
| 4 to under 10 | 2 (high) |
| 2 to under 4 | 1 (medium) |
| 1 to under 2 | 0.5 (low) |
| under 1 | 0.25 (minimal) |

3. If `avg_minutes_to_submit_claim` is 10 or more, move up one tier. 3 is the ceiling.

## Confidence

Confidence comes from how many interview participants (P1 to P6 in `interview_notes.md`) describe the problem the feature solves. The research lead mapped them:

| Feature | Participants | Why |
|---|---|---|
| Receipt photo capture with auto-fill | P1, P5 | P1 wants to "snap the receipt at the table". P5 wants the app to read the receipt and show the amount |
| Corporate card auto-match | P4 | Card statement amounts do not match what employees type |
| Approval reminders and escalation | P2 | Approves in a Friday batch, did not know about the delegate setting |
| Bulk approve for managers | P2 | Wants to approve the clean ones in bulk |
| Mobile offline drafts | P3 | Camera crashed and the draft was lost |
| Multi-currency conversion at entry | P4, P5 | AP fixes converted amounts by hand. P5 guesses the rate |
| Inline policy hints | P6 | "Tell me while I am filling it in" |
| Mileage tracker | none | Only tickets, no interview |

| Participants | Confidence |
|---|---|
| 2 or more | 100% (1.0) |
| exactly 1 | 80% (0.8) |
| none | 50% (0.5) |

## Effort

Person-months from engineering refinement on 2026-10-29. Includes design, build, test and rollout.

| Feature | Effort (person-months) | Notes from engineering |
|---|---|---|
| Receipt photo capture with auto-fill | 6 | New capture flow plus an OCR vendor. Vendor contract not signed yet |
| Corporate card auto-match | 5 | Needs the card feed from the bank partner |
| Approval reminders and escalation | 2 | Reuses the notification service. Needs the HR manager feed |
| Bulk approve for managers | 1.5 | Approval queue change only |
| Mobile offline drafts | 4 | Local storage on iOS and Android |
| Multi-currency conversion at entry | 3 | Needs a daily rate source |
| Inline policy hints | 2 | Reads `expense_policy.json` rules already used at submit time |
| Mileage tracker | 3 | New GPS permission on phones |

## Capacity

The Expense squad has **10 person-months** for the Q1 2027 MVP. A feature is in or out. No half features.

## MVP cut rule

Go down the list in RICE order. Add each feature if it still fits in the remaining capacity. If it does not fit, skip it and try the next one. Stop when nothing else fits.
