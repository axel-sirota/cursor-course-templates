# Lab 6 solution — Break It Yourself (contract gates)

Source lab: `materials/fragments/contract-hooks.html` (Demo 6 shows the shipped
violation; this lab has students plant their own).

- **Easy:** break a payments fixture against `contracts/refund.schema.json`, run the payments agent, and watch the Stop-hook gate block the stop and force the fix.
- **Hard:** add a required `"reason"` field to `NotificationEvent` and make the gate enforce the tightened contract end to end, failing existing fixtures until they carry a reason.

## Easy solution

Plant the violation (an enum break is ideal: obviously wrong to the validator,
plausible-looking to a human):

```bash
cd ~/labs/refund-monorepo
# in services/payments/fixtures/refund_result.json change:
#   "status": "approved"   ->   "status": "refunded"
```

Confirm the gate will fire before involving the agent — this is the same command the
Stop hook runs (executed 2026-07-24 on the scratch copy):

```bash
$ bash contracts/validate.sh services/payments; echo "exit=$?"
PASS fixtures/notification_approved.json
PASS fixtures/payment_completed.json
FAIL fixtures/refund_result.json: field "status" value "refunded" not in enum [approved, rejected].
PASS fixtures/refund_result_rejected.json
exit=2
```

Exit 2 is what blocks a stop. Now run the agent without hinting at the bug:

```text
claude
> Use the payments-implementer agent to verify your fixtures against the contract.
```

Expected transcript shape, matching the real Demo 6 run of the identical mechanism on
the notifications side (`materials/captured/demo6-gate-fail.txt`): the agent inspects
the fixtures, believes it is done, tries to stop, and its frontmatter `Stop` hook runs
`validate.sh services/payments` in the agent's own worktree:

```text
Stop hook feedback:
[bash "$CLAUDE_PROJECT_DIR"/contracts/validate.sh services/payments]: FAIL fixtures/refund_result.json: field "status" value "refunded" not in enum [approved, rejected].
```

The FAIL line lands in the agent's session verbatim; the agent edits the fixture back
to a legal enum value and its next stop attempt passes the gate
(`materials/captured/demo6-gate-pass.txt` shows the pass side):

```text
PASS fixtures/refund_result.json
```

Success criteria from the fragment, checked in the transcript: a blocked stop, the
FAIL feedback visible in-session, and a passing re-validation on the next attempt —
with the student never saying what was wrong.

After the run, `git diff` should show the fixture restored and nothing else; commit
or discard as the class prefers.

## Hard solution

Executed 2026-07-24 in a throwaway worktree pinned to the pre-Part-2 state
(`git worktree add /tmp/lab6-hard 165d144 --detach`) so the tightened contract could
be watched failing and then passing. On students' repos the state is whatever their
Demo/Lab progress left; the sequence is identical.

Step 1 — tighten the contract in `contracts/notification.schema.json`:

```diff
   "required": ["event_type", "payment_id", "refund_id", "recipient"],
+  "required": ["event_type", "payment_id", "refund_id", "recipient", "reason"],
   "properties": {
+    "reason": {
+      "type": "string"
+    },
```

Step 2 — the "extend `contracts/validate.py`" step is a trick: no code change is
needed. `validate.py` reads `required`, `type`, `enum`, and `minimum` generically
from whatever schema it loads, so the tightened schema is enforced the moment it is
saved. Real run against the untouched fixtures:

```bash
$ bash contracts/validate.sh services/notifications; echo "exit=$?"
FAIL fixtures/notification_event.json: field "reason" is required but missing.
exit=2
```

Students who dive into `validate.py` to add a special case should be redirected to
read `validate()` first — recognizing that the validator is schema-driven IS the
lesson of this tier. (If they instead added `reason` with an `enum` of allowed
identifiers, the enum check also enforces itself for free — same reasoning.)

Step 3 — make the fixtures carry a reason:

```diff
   "event_type": "refund.approved",
   "payment_id": "pay_001",
   "refund_id": "ref_001",
-  "recipient": "customer@example.com"
+  "recipient": "customer@example.com",
+  "reason": "refund_approved"
```

```bash
$ bash contracts/validate.sh services/notifications; echo "exit=$?"
PASS fixtures/notification_event.json
exit=0
```

Run end to end through the agent exactly as in the Easy tier: the notifications
agent's Stop hook now blocks until its fixtures (and any code emitting events) carry
the field.

Instructor reference: the scratch copy's history contains the full-scale version of
this change landed by the Demo 8 agent team — `e5b2fa4 contracts: add required
reason field to NotificationEvent`, followed by the payments and notifications
adaptations — so the end state is inspectable with
`git show e5b2fa4` if students want to compare.

## What students get wrong

1. **Breaking a field the validator does not check.** Renaming a fixture file or
   breaking a field with no `enum`/`type`/`minimum` rule gets `SKIP` (no schema
   matches the name) or `PASS`, and the student concludes gates do not work. The
   fixture must keep its `payment_*`/`refund_result*`/`notification_*` name and break
   a constraint the schema actually declares.
2. **Expecting the session to stop dead at the first FAIL.** The gate blocks the
   *agent's stop*, not the conversation; the agent keeps working until it satisfies
   the validator (at most 8 blocked stops — the cap was observed for real in the
   captured runs). Students who kill the session mid-loop never see the pass.
3. **In the Hard tier, editing schema and fixtures in one go.** Doing both at once
   means the gate never visibly fails, and the student has no evidence the tightened
   contract was ever enforced. Tighten first, run the validator, watch it fail, then
   fix the fixtures.

Verified: 2026-07-24 against sample-monorepo/python-fastapi
