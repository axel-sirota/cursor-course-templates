# BA-01: Set a monthly limit per category

**Epic:** E1 Category limits

**Goal:** G1

**Size:** S

## Story

As a household budgeter, I want to set a monthly limit for a spending category so that the app can tell me when I get close to it.

## Acceptance Criteria

### AC1: Save a new limit

- **Given** the Groceries category has no limit
- **When** the budgeter enters 400.00 and taps Save
- **Then** Groceries shows "Limit: $400.00" and the progress bar starts from this month's spending

### AC2: Lower a limit below current spending

- **Given** Groceries has a $400 limit and $350 spent this month
- **When** the budgeter changes the limit to 300.00 and taps Save
- **Then** the app saves the limit and shows "Over by $50.00" on Groceries

### AC3: Reject an invalid amount

- **Given** the limit editor is open for Dining
- **When** the budgeter enters 0 or a negative number
- **Then** Save is disabled and the field shows "Enter an amount above 0"

## Edge Cases

- EC3: a limit lowered below spending is covered by AC2. No alert is sent on save; BA-03 handles the next transaction.
- A category with no transactions this month shows 0% and still accepts a limit.

## INVEST Check

| Letter | Pass | Evidence |
|---|---|---|
| Independent | Yes | Ships alone. Alerts read limits but limits do not need alerts. |
| Negotiable | Yes | Editor layout is open. Only the outcome is fixed. |
| Valuable | Yes | The budgeter sees progress against a number they chose. |
| Estimable | Yes | Team sized it S in refinement. |
| Small | Yes | 3 AC, one screen. |
| Testable | Yes | Every Then is visible text on screen. |
