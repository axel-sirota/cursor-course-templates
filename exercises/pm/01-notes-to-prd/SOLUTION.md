# Exercise 1 Solution: Notes to PRD

Instructor key. Do not hand this to students before they finish. All counts below were recomputed from the shipped files.

## Step 1: ticket counts (support_tickets.csv, 60 rows)

| Category | Tickets | Share | Monthly tickets (usage_metrics.csv) |
|---|---|---|---|
| receipts | 21 | 35.0% | 229 (168 photo capture + 61 card match) |
| approvals | 15 | 25.0% | 160 (142 reminders and escalation + 18 bulk approve) |
| mobile | 9 | 15.0% | 97 |
| currency | 7 | 11.7% | 72 |
| policy | 7 | 11.7% | 83 |
| other | 1 | 1.7% | 12 |

Receipts plus approvals: 36 of 60 sampled tickets (60%), 389 of 653 monthly tickets (59.6%). The sample is 1 in 11, so 21 x 11 = 231 and 15 x 11 = 165, close to the monthly totals. The brief is right: receipts and approvals are the top two.

## Themes a good PRD must cite

### Receipts (21)

| Theme | Tickets | IDs |
|---|---|---|
| Blurry photo rejected, user gives up | 6 | T-1006, T-1017, T-1021, T-1026, T-1042, T-1055 |
| Emailed receipt not matched to the card transaction | 4 | T-1007, T-1031, T-1037, T-1053 |
| PDF receipt not supported | 4 | T-1040, T-1052, T-1054, T-1060 |
| Upload spins then fails, also on wifi | 3 | T-1014, T-1028, T-1057 |
| Hotel folio not read, every line typed by hand | 3 | T-1020, T-1029, T-1050 |
| Auto-fill read the tip line as the total ($56.83 short) | 1 | T-1051 |

### Approvals (15)

| Theme | Tickets | IDs |
|---|---|---|
| Manager on leave, nobody else can approve | 4 | T-1008, T-1016, T-1025, T-1059 |
| Many claims to approve, opening each takes forever (14 to 21 claims) | 4 | T-1013, T-1022, T-1024, T-1046 |
| Approved, but the employee still sees Pending | 3 | T-1030, T-1035, T-1036 |
| Claim waiting on manager for 21 or 27 days | 2 | T-1010, T-1027 |
| Reminder emails go to the old manager | 1 | T-1018 |
| Rejected with no comment | 1 | T-1019 |

### Interview evidence

| Area | Participants | Quote or fact to cite |
|---|---|---|
| Receipts | P1, P4 | P1 submits 4 to 6 weeks late, lost 2 receipts last quarter, "snap the receipt at the table". P4 sees duplicate submissions every week |
| Approvals | P2 | Approves 9 people in a Friday batch, "a minute or two each", wants bulk approve for clean claims, did not know about the delegate setting |
| Out of scope signals | P3 (mobile), P4 and P5 (currency), P6 (policy) | Good Non-goal material |

A strong PRD also notices that P2 "did not know there is a delegate setting": part of the "manager on leave" pain is discoverability, not a missing feature.

## Expected PRD content

### Problem (sample)

> Receipts and approvals cause 60% of Northwind Expense support tickets: 21 and 15 of 60 in the October sample, about 229 and 160 tickets a month. Employees give up on blurry photos (6 tickets), cannot upload PDFs (4) and retype hotel folios (3). Field staff like P1 hold receipts for 4 to 6 weeks and lose some. Approvers like P2 open every claim one by one, and when a manager is on leave nobody can approve (4 tickets). Claims that are approved still show Pending to the employee (3), which drives the "where is my money" email that P4 answers for two days after every payout run.

Must have: both counts, at least 3 theme counts, at least 3 participants, a cost (AP time, late submission, lost receipts).

### Goals (accept any with baseline, target, window)

| ID | Goal | Baseline source |
|---|---|---|
| G1 | Cut receipt-related tickets from 229 a month to 115 a month within 90 days of full rollout | usage_metrics.csv |
| G2 | Cut approval-related tickets from 160 a month to 80 a month within 90 days | usage_metrics.csv |
| G3 (optional) | Cut p90 submit-to-approve time from 7.0 days to 4.0 days within 90 days | expense_claims.csv (stretch) |

Reject: "faster approvals", "better receipts", any goal without a number.

### Epics (3)

| ID | Epic | Goal | Sample stories |
|---|---|---|---|
| E1 | Receipt capture that works | G1 | Retake guidance for a blurry photo; attach a PDF receipt; upload resumes after a dropped connection; confirm the auto-filled total before saving |
| E2 | Approval coverage and status | G2 | Name a delegate for leave dates; reminders go to the current manager; employee sees Approved within 1 minute of approval; rejection needs a reason |
| E3 | Approver throughput | G2 (or G3) | Approve all clean claims in one action; open the receipt inline without leaving the queue |

Also accepted: card match as its own epic (E2) with approvals merged into one epic, as long as there are exactly 3 and each points at a goal.

### Sample stories

**RAS-01: Retake a blurry receipt photo** (E1, G1, S)

As a field sales rep, I want the app to tell me the photo is blurry before I leave the table so that I can retake it instead of losing the receipt.

- AC1: **Given** a photo the reader scores as unreadable, **When** the rep taps Use photo, **Then** the app shows "This photo is blurry. Retake it?" with a Retake button and keeps the line as a draft.
- AC2: **Given** the rep retakes and the new photo is readable, **When** they tap Use photo, **Then** the receipt is attached and the merchant and total fields are filled in.
- AC3: **Given** the second photo is also unreadable, **When** they tap Use photo, **Then** the receipt is attached anyway, marked "Needs review", and the claim can still be submitted.

**RAS-02: Attach a PDF receipt** (E1, G1, S)

As an employee, I want to attach a PDF receipt so that I do not have to screenshot emailed invoices.

- AC1: **Given** a 1.4 MB PDF hotel folio, **When** the employee attaches it to a Lodging line, **Then** the PDF shows as page 1 thumbnail on the line.
- AC2: **Given** a 12 MB PDF, **When** they attach it, **Then** the app says "Files must be 10 MB or smaller" and nothing is attached.

**RAS-05: Name a delegate for leave** (E2, G2, S)

As an approver going on leave, I want to name a delegate for set dates so that my team's claims are not stuck.

- AC1: **Given** Dana set Lee as delegate from 2026-11-10 to 2026-11-21, **When** a $180.00 claim from Dana's report arrives on 2026-11-12, **Then** it appears in Lee's queue labeled "Delegated from Dana".
- AC2: **Given** Lee's approval limit is $2,500.00, **When** a $3,100.00 claim arrives, **Then** it routes to Dana's Director.

**RAS-08: Approve clean claims in bulk** (E3, G2, M)

As an engineering manager approving for 9 people, I want to approve every claim with no policy flags in one action so that I only open the flagged ones.

- AC1: **Given** 14 claims in the queue, 11 with no flags and 3 flagged, **When** the approver selects "Approve all clean (11)", **Then** the 11 claims move to Approved and the 3 flagged claims stay in the queue.
- AC2: **Given** one of the 11 claims is the approver's own claim, **When** they bulk approve, **Then** that claim is skipped with "You cannot approve your own claim".

Any AC that names a receipt rule must say "over $75.00" (`receipt_required_over_cents: 7500`). Any approval limit must match the policy: Manager $2,500.00, Director $10,000.00, VP $50,000.00.

### NFRs (sample, one per category)

| Category | Sample |
|---|---|
| Performance | p95 receipt upload under 3 s on 4G for files up to 10 MB. Approval status visible to the employee within 60 s of approval |
| Security | Receipt images Confidential, visible only to the submitter, their approvers and AP. Delegation is logged with who, when and dates |
| Privacy | Receipts kept 7 years for finance records, then deleted. No receipt image in notification text |
| Accessibility | Capture, upload and approval queue meet WCAG 2.2 AA. Bulk approve works by keyboard |
| Internationalization | Amounts in claim currency with ISO code (USD, EUR, GBP, CAD). Dates in the user's locale |
| Observability | `receipt_unreadable_total`, `receipt_upload_failed_total`, `approval_status_lag_seconds`. Alert at upload failures over 2% for 15 minutes |

### Edge cases (expect at least 5)

| Scenario | Story |
|---|---|
| Second photo still blurry | RAS-01 |
| PDF over 10 MB, or a multi-page folio | RAS-02 |
| Connection drops mid-upload (T-1014 "tried on wifi too") | upload story |
| Auto-fill reads the tip line as the total (T-1051) | confirm-total story |
| Delegate is also on leave, or delegate limit too low | RAS-05 |
| Bulk selection includes the approver's own claim | RAS-08 |
| Reminder sent after the manager changed (T-1018) | reminders story |
| Expense exactly $75.00 (no receipt needed) | any receipt-rule story |

### Non-goals (expect at least 3, each with a reason)

Mobile offline drafts (9 tickets, P3), multi-currency conversion (7 tickets, P4, P5), inline policy hints (7 tickets, P6), duplicate detection (P4), travel booking. Each needs a reason, for example "separate PRD next quarter" or "smaller pain by ticket count".

## Stretch answers

| Question | Answer |
|---|---|
| Submit-to-approve time from `expense_claims.csv` | 3,589 approved or paid claims. Median 3.6 days, p90 7.0 days. The 21 and 27 day tickets are outliers. Use the median or p90 as the baseline, and treat long waits as an edge case (manager on leave) |
| Expense date to submission (expense_lines.csv joined to claims) | Median 8 days, p90 15 days. P1's 4 to 6 weeks is the tail, not the norm |
| Duplicates | 90 exact duplicate lines and 45 near-duplicates. Reasonable either way, but a fourth epic breaks "exactly 3". Expect a decision record that makes it a Non-goal or a follow-up PRD |

## Grading

| Level | What it looks like |
|---|---|
| Pass | Counts 21 and 15 correct, 3 epics with goals, every goal measurable, `/pm-validate` Yes |
| Strong | Cites at least 8 of the 12 themes with counts or IDs, 3 or more participants, edge cases from real tickets, policy numbers exact |
| Common misses | Goals without baselines, stories like "improve OCR", a receipt rule of "$50" or "receipts always required", forgetting the delegate discoverability point |
