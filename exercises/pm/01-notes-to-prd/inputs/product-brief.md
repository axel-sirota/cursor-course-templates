# Product brief: Northwind Expense

Paste these five lines at the top of `workspaces/pm/plans/interface-contract.md` so every session knows the product.

1. **Product:** Northwind Expense, the expense app of the fictional Northwind Co. Employees file claims (expense lines plus receipts), managers approve them, Finance AP pays them in a weekly Thursday payout run.
2. **Users:** employees who file claims (phone and laptop), approvers in the submitter's management chain, AP specialists at Northwind. Customer companies use the same app.
3. **Policy:** `exercises/_data/northwind/expense_policy.json` is the source of truth. Receipt required over $75.00, claims older than 60 days are rejected, Manager approval limit $2,500.00, Director $10,000.00.
4. **Evidence:** six user interviews (P1 to P6) and a 1-in-11 sample of October support tickets (60 tickets). Monthly totals per feature area are in `usage_metrics.csv`.
5. **Constraints:** synthetic data only. Currencies USD, EUR, GBP, CAD. No change to the approval rules in this PRD.
