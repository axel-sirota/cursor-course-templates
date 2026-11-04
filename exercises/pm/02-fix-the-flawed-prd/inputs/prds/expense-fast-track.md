# PRD: Expense Fast Track

| Field | Value |
|---|---|
| Owner | PM, Expense squad |
| Status | Draft |
| Last updated | 2026-10-30 |
| Product | Northwind Expense, internal expense app of the fictional Northwind Co. |

## Problem

Employees at Northwind and at customer companies say the expense app is slow and annoying.
Receipts are the top complaint in support, and approvals are second.
People wait too long to get their money back.
Source: [research/interview_notes.md](../research/interview_notes.md).

## Goals

- **G1:** Cut receipt-related support tickets from 229 per month to 120 per month within 90 days of full rollout.
- **G2:** Make approvals faster and keep managers happy.

## Users

| User | Context |
|---|---|
| Employee | Files claims from a phone or a laptop. |
| Approver | A manager who approves claims for their team. |
| AP specialist | Finance staff at Northwind who pay approved claims. |

## Epics

| ID | Epic | Goal | Stories |
|---|---|---|---|
| E1 | Receipt capture | G1 | EFT-01, EFT-02, EFT-03 |
| E2 | Faster approvals | G2 | EFT-04 |
| E3 | Corporate travel booking | G1 | EFT-06 |

## User Stories

| ID | Title | Epic | Size | File |
|---|---|---|---|---|
| EFT-01 | Rebuild the receipt experience | E1 | XL | [expense-fast-track-01-receipt-experience.md](../stories/expense-fast-track-01-receipt-experience.md) |
| EFT-02 | Add receipt status column | E1 | S | [expense-fast-track-02-receipt-status-column.md](../stories/expense-fast-track-02-receipt-status-column.md) |
| EFT-03 | Upload a receipt | E1 | S | [expense-fast-track-03-upload-receipt.md](../stories/expense-fast-track-03-upload-receipt.md) |
| EFT-04 | Better approval screen | E2 | M | [expense-fast-track-04-approval-screen.md](../stories/expense-fast-track-04-approval-screen.md) |
| EFT-05 | Delegate approvals during leave | E2 | S | [expense-fast-track-05-delegate-approvals.md](../stories/expense-fast-track-05-delegate-approvals.md) |

## Policy rules this PRD relies on

- Receipts are required for any expense over $50.
- A Manager can approve claims up to $5,000. Larger claims go to a Director.
- Claims older than 60 days are rejected.

## Non-functional Requirements

### Performance

- **NFR-PERF-1:** The app should be fast, especially receipt upload.

### Security

- **NFR-SEC-1:** Receipt images are Confidential (level 2 of 4) and are only visible to the submitter, their approvers and AP.

### Privacy

- **NFR-PRIV-1:** Receipt images are kept for 7 years to match the finance record retention rule, then deleted.

### Internationalization

- **NFR-I18N-1:** Amounts show in the claim currency (USD, EUR, GBP, CAD) with the ISO code next to the number.

### Observability

- **NFR-OBS-1:** Emit `receipt_upload_failed_total` and `approval_latency_hours`. Alert if upload failures exceed 2% over 30 minutes.

## Edge Cases

| ID | Scenario | Handled by |
|---|---|---|
| EC1 | None. This PRD covers the happy path. | n/a |

## Dependencies

| Dependency | Owner | Needed for |
|---|---|---|
| OCR vendor contract | Procurement | EFT-01 |
| HR system feed with each employee's current manager | People systems squad | EFT-04, EFT-05 |
| Travel agency booking API | Partnerships | EFT-06 |

## Rollout Plan

1. Week 1: Northwind staff only, behind the `fast_track` feature flag.
2. Week 3: 25% of customer companies. Watch NFR-OBS-1.
3. Week 5: 100% of customer companies.
4. Rollback: turn the flag off. Saved receipts stay attached to their claims.

## Success Metrics

| Metric | Baseline | Target | Window | Goal |
|---|---|---|---|---|
| Receipt-related support tickets per month | 229 | 120 | 90 days after 100% rollout | G1 |
| Approval speed | TBD | Better | TBD | G2 |

## Open Questions

| ID | Question | Owner | Due |
|---|---|---|---|
| Q1 | Which OCR vendor do we use? | Engineering lead | 2026-11-20 |
