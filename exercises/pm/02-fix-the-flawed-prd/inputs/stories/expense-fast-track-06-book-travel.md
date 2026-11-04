# EFT-06: Book flights and hotels in the app

**Epic:** E3 Corporate travel booking

**Goal:** G1

**Size:** L

## Story

As an employee who travels, I want to book flights and hotels inside Northwind Expense so that the receipt is already in the app when the trip ends.

## Acceptance Criteria

### AC1: Booking creates a claim line

- **Given** an employee books a $420.00 economy flight through the in-app booking page
- **When** the travel agency confirms the booking
- **Then** a draft Airfare line of $420.00 with the e-ticket attached appears in the employee's next claim

## Edge Cases

- The booking is cancelled after the line was created.

## INVEST Check

| Letter | Pass | Evidence |
|---|---|---|
| Independent | No | Needs the travel agency booking API. |
| Negotiable | Yes | Agency is not chosen yet. |
| Valuable | Yes | No receipt to lose. |
| Estimable | No | No API docs yet. |
| Small | No | New booking flow. |
| Testable | Yes | AC1 names the line created. |
