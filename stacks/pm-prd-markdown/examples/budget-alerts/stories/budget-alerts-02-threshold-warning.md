# BA-02: Warn at 80% of a limit

**Epic:** E2 Alert delivery

**Goal:** G1

**Size:** M

## Story

As a light tracker, I want a push alert when a category reaches 80% of its limit so that I can slow down before I overspend.

## Acceptance Criteria

### AC1: First crossing sends one warning

- **Given** Dining has a $200 limit, $150 spent, and alerts are on
- **When** a $15.00 Dining transaction posts
- **Then** the budgeter gets one push alert: "Dining is at 83% of $200. $35.00 left this month."

### AC2: No repeat warning in the same month

- **Given** a Dining 80% warning was already sent this month
- **When** another $5.00 Dining transaction posts and spending stays under 100%
- **Then** no new alert is sent

### AC3: Refund resets the warning

- **Given** Dining is at 83% and the warning was sent
- **When** a $30.00 refund posts and spending drops to 68%
- **Then** the next crossing of 80% this month sends a new warning

### AC4: Push permission is off

- **Given** the budgeter turned off notifications for the app in phone settings
- **When** Dining crosses 80%
- **Then** the alert appears in the in-app Alerts inbox with an unread badge

## Edge Cases

- EC1: refund drops spending back under 80%, covered by AC3.
- EC5: push permission off at the operating system level, covered by AC4.
- A transaction that jumps past 100% sends only the BA-03 alert, not both.

## INVEST Check

| Letter | Pass | Evidence |
|---|---|---|
| Independent | Yes | Needs limits from BA-01, which ships in an earlier sprint. |
| Negotiable | Yes | Threshold is a default, see the decision record. Wording is open. |
| Valuable | Yes | Light trackers hear about trouble without opening the app. |
| Estimable | Yes | Team sized it M in refinement. |
| Small | Yes | 4 AC, one alert type, fits one sprint. |
| Testable | Yes | Each Then is a sent or not-sent alert with exact text. |
