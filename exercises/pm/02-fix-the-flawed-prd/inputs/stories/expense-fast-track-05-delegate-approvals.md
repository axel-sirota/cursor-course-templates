# EFT-05: Delegate approvals during leave

**Epic:** E5 Approver coverage

**Goal:** G2

**Size:** S

## Story

As an approver going on leave, I want to name a delegate for set dates so that my team's claims are not stuck while I am away.

## Acceptance Criteria

### AC1: Delegate gets new claims

- **Given** Dana (Manager) set Lee as delegate from 2026-11-10 to 2026-11-21
- **When** a report of Dana's submits a $180.00 claim on 2026-11-12
- **Then** the claim appears in Lee's approval queue with the label "Delegated from Dana"

### AC2: Delegate limit is checked

- **Given** Lee is a Manager with a $2,500.00 approval limit and is Dana's delegate
- **When** a $3,100.00 claim arrives during the delegation dates
- **Then** the claim goes to Dana's Director, not to Lee

### AC3: Delegation ends

- **Given** the delegation ended on 2026-11-21
- **When** a new claim is submitted on 2026-11-24
- **Then** the claim goes to Dana's queue, and Lee no longer sees it

## Edge Cases

- A delegate cannot approve their own claim, even inside the delegation dates. Covered by AC2 routing rules.
- The delegate is also on leave on the same dates.

## INVEST Check

| Letter | Pass | Evidence |
|---|---|---|
| Independent | Yes | Needs the HR manager feed only. |
| Negotiable | Yes | Date picker and label wording are open. |
| Valuable | Yes | 4 of 15 sampled approval tickets are "manager is on leave". |
| Estimable | Yes | Sized S in refinement. |
| Small | Yes | 3 AC, one setting. |
| Testable | Yes | Each Then names the queue the claim lands in. |
