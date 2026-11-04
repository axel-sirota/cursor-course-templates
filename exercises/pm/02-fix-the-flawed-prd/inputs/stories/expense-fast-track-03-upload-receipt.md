# EFT-03: Upload a receipt

**Epic:** E1 Receipt capture

**Goal:** G1

**Size:** S

## Story

As an employee, I want to attach a receipt to an expense line from my laptop so that my claim is not sent back for a missing receipt.

## Acceptance Criteria

### AC1: Upload works

- User uploads a JPG or PNG receipt and it works.
- The receipt shows on the line.

### AC2: Receipt required

- **Given** a Meals line of $62.00 with no receipt attached
- **When** the employee presses Submit
- **Then** the claim is blocked with the message "A receipt is required for expenses over $50."

## Edge Cases

- File bigger than 10 MB.

## INVEST Check

| Letter | Pass | Evidence |
|---|---|---|
| Independent | Yes | Laptop upload already exists for JPG. |
| Negotiable | Yes | File types can change. |
| Valuable | Yes | Fewer bounced claims. |
| Estimable | Yes | Sized S. |
| Small | Yes | One screen. |
| Testable | Yes | Upload a file. |
