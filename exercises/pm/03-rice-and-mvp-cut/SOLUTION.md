# Exercise 3 Solution: RICE and the MVP Cut

Instructor key. Do not hand this to students before they finish. Every number below was computed from `usage_metrics.csv` and `inputs/effort-estimates.md` with a script, then checked by hand for the boundary rows.

## RICE table

| Rank | Feature | Reach | Tickets per 1,000 users | Minutes to submit | Impact | Confidence | Effort | RICE |
|---|---|---|---|---|---|---|---|---|
| 1 | Inline policy hints | 38,500 | 2.16 | 8.7 | 1 | 0.8 | 2 | 15,400.0 |
| 2 | Approval reminders and escalation | 12,300 | 11.54 | 7.8 | 3 | 0.8 | 2 | 14,760.0 |
| 3 | Receipt photo capture with auto-fill | 41,200 | 4.08 | 9.4 | 2 | 1.0 | 6 | 13,733.3 |
| 4 | Mobile offline drafts | 19,800 | 4.90 | 11.2 | 3 (2, +1 for minutes) | 0.8 | 4 | 11,880.0 |
| 5 | Multi-currency conversion at entry | 6,400 | 11.25 | 13.6 | 3 (ceiling) | 1.0 | 3 | 6,400.0 |
| 6 | Corporate card auto-match | 27,900 | 2.19 | 6.1 | 1 | 0.8 | 5 | 4,464.0 |
| 7 | Bulk approve for managers | 4,100 | 4.39 | 7.1 | 2 | 0.8 | 1.5 | 4,373.3 |
| 8 | Mileage tracker | 8,900 | 1.35 | 5.2 | 0.5 | 0.5 | 3 | 741.7 |

## MVP cut (rule as written, 10 person-months)

| Step | Feature | Effort | Used | Decision |
|---|---|---|---|---|
| 1 | Inline policy hints | 2 | 2 | In |
| 2 | Approval reminders and escalation | 2 | 4 | In |
| 3 | Receipt photo capture with auto-fill | 6 | 10 | In |
| 4 to 8 | Everything else | 1.5 to 5 | 10 | Out, no capacity left |

**MVP: Inline policy hints, Approval reminders and escalation, Receipt photo capture with auto-fill. 10 of 10 person-months. Total RICE 43,893.3.**

## Traps

| Trap | What goes wrong | Effect |
|---|---|---|
| Receipt photo capture is at 4.08 tickets per 1,000, just over the 4 boundary | Rounding to 4.1 is fine. Reading it as "under 4" gives Impact 1 and RICE 6,866.7 | Drops to rank 4. The cut becomes policy, approvals, mobile, bulk (9.5) |
| Mobile offline drafts gets the minutes bump (11.2 is 10 or more) | Forgetting the bump gives Impact 2 and RICE 7,920.0 | Ranks 4th either way. Cut unchanged, but the score is wrong |
| Multi-currency is already at Impact 3 | Bumping it to "4" | Not allowed, 3 is the ceiling |
| Confidence as a percent | Using 80 instead of 0.8 | Every score x100. Ranking unchanged. Accept if consistent, but ask for the decimal form |
| Reach in thousands | Using 41.2 instead of 41,200 | Scores / 1,000. Ranking unchanged. Accept if consistent |
| Receipts is the top pain area by tickets (229 a month) but only rank 3 | Students "fix" the score so receipts ranks 1 | The rule is the rule. The argument belongs in the risks section |

## What the score does not see (expected points)

1. **The cut is not the best set by total RICE.** Policy hints + approval reminders + mobile offline drafts + bulk approve uses 9.5 person-months and totals 46,413.3, which beats the rule's cut (43,893.3) by 2,520. The greedy rule spends 6 of 10 months on one feature. This is the best possible set in 10 person-months (checked over all 255 combinations).
2. **Receipt photo capture has the most delivery risk.** 6 person-months and an OCR vendor contract that is not signed. If the contract slips, 60% of the quarter is blocked.
3. **Dependencies.** Approval reminders need the HR manager feed (also fixes T-1018, reminders to the old manager). Card auto-match needs a bank card feed.
4. **Bulk approve pairs with approval reminders.** Same queue, same users (P2), 1.5 person-months.
5. **Evidence is thin for most features.** Six interviews total. Five features rest on one participant.

Either final call is acceptable if it is argued with numbers:

- **Keep the rule's cut:** receipts are the largest pain by ticket volume, and the rule is what the team agreed.
- **Recommend the alternative cut:** more total value, lower delivery risk, and receipt capture moves to Q2 once the vendor contract is signed.

## Sensitivity (stretch answers)

| Change | Mobile RICE | New rank | Cut under the rule |
|---|---|---|---|
| None | 11,880.0 | 4 | Policy, Approvals, Receipt (10) |
| Mobile Confidence 100% (one more interview) | 14,850.0 | 2 | Policy, Mobile, Approvals, Bulk (9.5) |
| Mobile Effort 3 | 15,840.0 | 1 | Mobile, Policy, Approvals, Multi-currency (10) |

Multi-currency (6,400.0) would need Effort under 1.4 person-months to outrank receipt photo capture at the current Reach. Its Impact and Confidence are already at the maximum, so the lever is Reach: only 6,400 users touch currency each month. That is the one sentence for the head of Finance.

## Sample stakeholder update

> **Decision.** For Q1 2027 the Expense squad ships inline policy hints, approval reminders with escalation, and receipt photo capture with auto-fill: 10 of our 10 person-months.
>
> **Why these.** They are the top 3 of 8 candidates by RICE. Policy hints reach 38,500 users a month and fix the "tell me while I am filling it in" problem (P6). Approval reminders cut the worst ticket rate we have, 11.5 tickets per 1,000 users, including "my manager is on leave" (4 of 15 sampled approval tickets). Receipt capture reaches 41,200 users and is the largest ticket area, 229 a month.
>
> **What is out.** Mobile offline drafts (rank 4): next in line, revisit when receipt capture is in beta. Multi-currency (rank 5): high pain but only 6,400 users. Card auto-match (rank 6): needs a bank card feed. Bulk approve (rank 7): small, first candidate for spare capacity. Mileage tracker (rank 8): no interview evidence.
>
> **Risks.** The OCR vendor contract is not signed. Receipt capture is 6 of 10 months (owner: engineering lead, decision by 2026-11-20). Approval reminders depend on the HR manager feed (owner: People systems squad).
>
> **Ask.** Sign the OCR vendor contract by 2026-11-20, or approve the alternative cut (mobile drafts and bulk approve instead of receipt capture), which scores 6% higher in total RICE.

## Grading

| Level | What it looks like |
|---|---|
| Pass | All 8 scores match to one decimal, cut is policy hints + approval reminders + receipt capture, update is one page and starts with the decision |
| Strong | Finds the 46,413.3 alternative, names the vendor risk, makes a clear recommendation with an owner and a date |
| Common misses | Receipt Impact 1 (boundary), no minutes bump for mobile, a stakeholder update that opens with method instead of the decision |
