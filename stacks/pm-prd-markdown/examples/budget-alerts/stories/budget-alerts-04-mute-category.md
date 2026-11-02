# BA-04: Mute alerts for one category

**Epic:** E3 Alert controls

**Goal:** G2

**Size:** S

## Story

As a household budgeter, I want to mute alerts for one category so that the alerts I still get are the ones I act on.

## Acceptance Criteria

### AC1: Mute a category

- **Given** alerts are on for Dining and Groceries
- **When** the budgeter turns off "Alerts" on the Dining detail screen
- **Then** Dining shows "Alerts muted" and Groceries alerts keep arriving

### AC2: Muted category goes over its limit

- **Given** Dining alerts are muted and Dining has a $200 limit with $195 spent
- **When** a $20.00 Dining transaction posts
- **Then** no push alert is sent and the Budget tab still shows Dining as "Over by $15.00"

### AC3: Unmute restores alerts next crossing

- **Given** Dining alerts are muted and Dining is at 85%
- **When** the budgeter turns Dining alerts back on
- **Then** no alert is sent for the past crossing, and the next threshold crossing this month sends one

## Edge Cases

- EC4: a muted category exceeds its limit, covered by AC2.
- Muting every category is allowed. The settings screen then shows "All alerts muted" with a 1-tap undo.

## INVEST Check

| Letter | Pass | Evidence |
|---|---|---|
| Independent | Yes | Changes alert eligibility only. No new alert type. |
| Negotiable | Yes | Placement of the toggle is open. |
| Valuable | Yes | Fewer unwanted alerts keeps opt-out under 10% (G2). |
| Estimable | Yes | Team sized it S in refinement. |
| Small | Yes | 3 AC, one toggle. |
| Testable | Yes | Each Then is a sent or not-sent alert or visible label. |
