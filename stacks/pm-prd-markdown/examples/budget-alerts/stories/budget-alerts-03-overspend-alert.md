# BA-03: Alert when a limit is exceeded

**Epic:** E2 Alert delivery

**Goal:** G1

**Size:** S

## Story

As a household budgeter, I want an alert the moment a category goes over its limit so that I can move money from another category before payday.

## Acceptance Criteria

### AC1: Crossing 100% sends an overspend alert

- **Given** Groceries has a $400 limit and $390 spent
- **When** a $25.00 Groceries transaction posts
- **Then** the budgeter gets one push alert: "Groceries is over by $15.00. Tap to adjust your plan."

### AC2: A single large transaction skips the warning

- **Given** Groceries has a $400 limit and $200 spent, and no 80% warning was sent
- **When** a $250.00 Groceries transaction posts
- **Then** only the overspend alert is sent, with "over by $50.00"

### AC3: Tapping the alert opens the category

- **Given** the budgeter received an overspend alert for Groceries
- **When** they tap the alert
- **Then** the app opens the Groceries detail screen with the limit editor visible

## Edge Cases

- EC2: one transaction jumps from 50% past 100%, covered by AC2.
- EC3: a limit lowered below spending sends no alert on save. The next Groceries transaction triggers AC1.

## INVEST Check

| Letter | Pass | Evidence |
|---|---|---|
| Independent | Yes | Uses the same transaction events as BA-02 but ships on its own. |
| Negotiable | Yes | Alert wording and deep-link target are open. |
| Valuable | Yes | The budgeter can rebalance the same day, not at month end. |
| Estimable | Yes | Team sized it S in refinement. |
| Small | Yes | 3 AC, one alert type. |
| Testable | Yes | Each Then is an exact alert text or screen. |
