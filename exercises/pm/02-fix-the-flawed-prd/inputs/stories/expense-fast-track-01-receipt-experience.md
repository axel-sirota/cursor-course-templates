# EFT-01: Rebuild the receipt experience

**Epic:** E1 Receipt capture

**Goal:** G1

**Size:** XL

## Story

As an employee, I want the whole receipt experience rebuilt with photo capture, PDF upload, email forwarding, card matching and auto-fill so that receipts are never a problem again.

## Acceptance Criteria

### AC1: Photo capture works

- **Given** an employee on the phone app
- **When** they take a photo of a receipt
- **Then** the receipt is attached, the total is read, the merchant is read, the card transaction is matched and the claim line is filled in

### AC2: PDF and email work

- **Given** an employee with a PDF receipt or an emailed receipt
- **When** they upload it or forward it to receipts@northwind.example
- **Then** it works the same as a photo

## Edge Cases

- Covered by the AC above.

## INVEST Check

| Letter | Pass | Evidence |
|---|---|---|
| Independent | Yes | Self-contained. |
| Negotiable | Yes | Details can change. |
| Valuable | Yes | Receipts are the top complaint. |
| Estimable | Yes | Big, but the team has done receipts before. |
| Small | Yes | One feature area. |
| Testable | Yes | Has AC. |
