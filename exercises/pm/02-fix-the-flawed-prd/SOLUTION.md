# Exercise 2 Solution: Fix the Flawed PRD

Instructor key. Do not hand this to students before they finish.

## Seeded defects (16)

Line numbers refer to the files in `inputs/` as shipped. "Script" means `check_prd.py` flags it. "Agent" means only a reader (`/pm-validate`, the student, the instructor) can find it.

| # | File | Line | Defect | Rule broken | Found by | Expected fix |
|---|---|---|---|---|---|---|
| 1 | `prds/expense-fast-track.md` | 12 to 15 | Problem has no numbers: no who, how often, or cost. "Slow and annoying", "too long" | Problem cites evidence (template, style rule) | Agent | Rewrite with ticket counts: receipts 21 of 60 sampled tickets (35%, about 229 a month), approvals 15 of 60 (25%, about 160 a month). Cite P1, P2, P4 |
| 2 | `prds/expense-fast-track.md` | 20 | G2 "Make approvals faster and keep managers happy" has no metric, baseline or window | Goals: baseline to target, time window | Agent | e.g. "Cut approval-related tickets from 160 a month to 90 a month within 90 days" or "p90 submit-to-approve time from 7.0 days to 3 days" |
| 3 | `prds/expense-fast-track.md` | after 20 (missing) | No `## Non-goals` section | Required heading | **Script** | Add Non-goals. At least: travel booking (moved from E3), multi-currency, mobile offline drafts, each with a reason |
| 4 | `prds/expense-fast-track.md` | 36, plus `stories/...-06-book-travel.md` | E3 "Corporate travel booking" is scope creep. No ticket or interview asks for it. Traced to G1 so it looks legitimate | Scope follows the problem | Agent | Delete E3 and EFT-06, move to Non-goals ("separate PRD, needs an agency contract") |
| 5 | `stories/...-05-delegate-approvals.md` | 3 (and PRD 35, 46) | EFT-05 says `Epic: E5`, which is not in the Epics table. The index row says E2 and the E2 row does not list EFT-05 | Story traces to an epic | **Script** (E5 missing) | Set `**Epic:** E2 Faster approvals`, add EFT-05 to the E2 row |
| 6 | `prds/expense-fast-track.md` | 40 to 46 | `expense-fast-track-06-book-travel.md` exists but is not in the User Stories index (the Epics table lists it) | Every story file has an index row | **Script** | Resolved by the fix to #4 (delete the story) |
| 7 | `prds/expense-fast-track.md` and `stories/...-03-upload-receipt.md` | PRD 50, story 20 to 24 | Receipt threshold stated as "over $50". Policy: `receipt_required_over_cents: 7500`, so over $75.00. The AC blocks a $62.00 lunch that policy allows | Policy is the source of truth | Agent | "over $75.00". Rewrite AC2 with an amount above $75 (e.g. $82.40) and add a case at exactly $75.00 that does not need a receipt |
| 8 | `prds/expense-fast-track.md` | 51 | "A Manager can approve claims up to $5,000". Policy: Manager `250000` cents = $2,500.00 (Director $10,000) | Policy is the source of truth | Agent | "$2,500.00". Note EFT-05 AC2 already uses $2,500 correctly, so the PRD contradicts its own story |
| 9 | `prds/expense-fast-track.md` | 58 | NFR-PERF-1 "The app should be fast" has no number | NFR has a number or named standard | Agent (strict mode misses it, see below) | e.g. "p95 receipt upload under 3 s on 4G for files up to 10 MB; auto-fill result shown in under 5 s at p95" |
| 10 | `prds/expense-fast-track.md` | between 64 and 68 (missing) | No `### Accessibility` NFR | Required NFR heading | **Script** | "Capture, upload and approval screens meet WCAG 2.2 AA" |
| 11 | `prds/expense-fast-track.md` | 80 | Edge Cases says "None. This PRD covers the happy path" | Edge cases are explicit, happy path only is incomplete | Agent | At least 5, from the tickets: blurry photo (6 tickets), PDF receipt (4), upload fails on wifi (3), tip line read as total (1), approver on leave (4), approved but still shows pending (3) |
| 12 | `prds/expense-fast-track.md` | 102 | Success metric "Approval speed / TBD / Better / TBD" | Metric has baseline, target, window | Agent | Same metric as the fixed G2, with the baseline from the data |
| 13 | `stories/...-01-receipt-experience.md` | 7, 11, 39 | Too big: XL, five capabilities (photo, PDF, email, card match, auto-fill) in one story. INVEST self-check says "Small: Yes" | INVEST Small, Estimable | Agent | Split into at least: photo capture, PDF upload, card match, auto-fill with a confirm step. Each S or M, new IDs EFT-07 onward |
| 14 | `stories/...-02-receipt-status-column.md` | 1, 11, 15 to 19 | Implementation-led: "As a developer, I want to add a `receipt_status` column". No user value, AC checks a schema | Stories from the user perspective, no implementation | Agent (the story line passes the format check) | Delete it or rewrite as "As an employee, I want to see whether my receipt was read so that I know if I must type the amounts" with a user-visible AC |
| 15 | `stories/...-03-upload-receipt.md` | 15 to 18 | AC1 is two plain bullets ("it works"), no Given/When/Then | AC format | **Script** | Given a 2.1 MB PNG receipt, When the employee attaches it to a line, Then a thumbnail shows on that line within 3 s |
| 16 | `stories/...-04-approval-screen.md` | 11, 19, 25 | Not testable: "better approval screen", Then "feels faster and more intuitive", "happier than before" | INVEST Testable, one observable outcome per Then | Agent | Pick one capability (e.g. bulk approve clean claims, from P2 and 4 "opening each one takes forever" tickets). Then: "the 12 selected claims move to Approved and leave the queue" |

Script finds 5 (#3, #5, #6, #10, #15). Agent or human review is needed for the other 11.

### Bonus findings (credit, not required)

| File | Line | Finding |
|---|---|---|
| `stories/...-01-receipt-experience.md` | 29 | "Covered by the AC above" is not an edge case list |
| `stories/...-05-delegate-approvals.md` | 35 | Says self-approval is "covered by AC2", but AC2 is about the approval limit. Needs its own AC |
| `stories/...-06-book-travel.md` | 29, 32, 33 | Its own INVEST check fails I, E and S, yet it is in the PRD |
| `stories/...-02-receipt-status-column.md` | 30 | "Negotiable: No" admits the story is a fixed implementation |
| `stories/...-03-upload-receipt.md` | 11 vs ticket data | Laptop JPG upload already exists. The 4 PDF tickets (T-1040, T-1052, T-1054, T-1060) say PDF is the gap, but AC1 still lists JPG and PNG only |

### Traps (not defects)

- PRD line 52 "Claims older than 60 days are rejected" is correct (`max_age_days: 60`). Students who "fix" it lose the point.
- EFT-05 is the best story in the set. Its only defect is the wrong epic. Students who rewrite it wasted time.

## Script output on the shipped inputs

```
$ python3 stacks/pm-prd-markdown/examples/budget-alerts/scripts/check_prd.py exercises/pm/02-fix-the-flawed-prd/inputs
FAIL prds/expense-fast-track.md: missing required heading '## Non-goals'
FAIL prds/expense-fast-track.md: missing NFR heading '### Accessibility'
FAIL stories/expense-fast-track-03-upload-receipt.md: 'AC1: Upload works' (line 15) lacks **Given**, **When**, **Then**
FAIL stories/expense-fast-track-05-delegate-approvals.md: epic E5 is not in the PRD Epics table
FAIL prds/expense-fast-track.md: User Stories index does not link expense-fast-track-06-book-travel.md

5 failure(s) in default mode.
```

`--strict` prints the same 5. It does not flag NFR-PERF-1 "should be fast": the strict rule looks for any digit in the NFR subsection, and the ID `NFR-PERF-1` contains one. That is the answer to the first stretch question, and a good class discussion on why a pass from a script is not a review.

## Grading

| Level | What it looks like |
|---|---|
| Pass | 12 or more of the 16 found, all policy numbers fixed from `expense_policy.json`, `/pm-validate` says Yes |
| Strong | All 16, the mega-story split into 4 or more stories with new IDs, edge cases mapped to ticket IDs, at least 2 bonus findings |
| Common misses | #7 and #8 (students trust the PRD's numbers), #4 (travel booking sounds useful), #14 (the line passes every format hook) |
