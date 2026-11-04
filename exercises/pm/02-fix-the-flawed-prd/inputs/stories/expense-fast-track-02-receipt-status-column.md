# EFT-02: Add receipt status column

**Epic:** E1 Receipt capture

**Goal:** G1

**Size:** S

## Story

As a developer, I want to add a `receipt_status` column to the `expense_lines` table so that we can store whether a receipt was read.

## Acceptance Criteria

### AC1: Column exists

- **Given** the production database
- **When** the migration runs
- **Then** `expense_lines` has a `receipt_status` column of type `varchar(20)` with a default of `pending`

## Edge Cases

- The migration must not lock the table for more than 1 second.

## INVEST Check

| Letter | Pass | Evidence |
|---|---|---|
| Independent | Yes | Only touches one table. |
| Negotiable | No | Column name agreed with the data team. |
| Valuable | Yes | Needed by EFT-01. |
| Estimable | Yes | Half a day. |
| Small | Yes | One migration. |
| Testable | Yes | Check the schema. |
