# Decision: Default warning threshold is 80%

| Field | Value |
|---|---|
| Date | 2026-10-20 |
| Owner | PM, Budgeting squad |
| Affects | BA-02 |

## Context

Budgeters need a warning early enough to change behavior, but not so early that it feels like noise.

## Options

| Option | For | Against |
|---|---|---|
| 75% | More time to react | Fires in week 2 for most grocery budgets |
| 80% | Matches what 64% of survey users picked | Less time in short months |
| User picks per category | Fits every budget | Adds a setting before anyone has used alerts |

## Decision

Ship 80% as a fixed default in v1. Revisit a per-category setting after 60 days of opt-out data.
