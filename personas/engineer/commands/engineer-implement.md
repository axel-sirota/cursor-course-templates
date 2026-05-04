# /engineer-implement

Execute the TDD loop on a tasks file produced by `/engineer-tasks`. Delegates to subagents.

## Prerequisites

- A `docs/tasks-{feature}.md` file must exist. Ask for the feature name if not specified.
- All task dependencies must be resolved before a task begins.

## Per-Task Loop (execute in dependency order)

### 1. Red — Write the Failing Test

Write a test that asserts the task's acceptance criteria. Run it and confirm it fails for the expected reason (not a syntax error or import failure).

### 2. Run — Confirm Expected Failure

Invoke the `test-runner` subagent. The test must fail — if it passes without implementation, the test is wrong. Fix the test and repeat.

### 3. Green — Write Minimum Implementation

Write the simplest code that makes the test pass. Do not over-engineer at this stage.

### 4. Run — Confirm Pass + No Regression

Invoke `test-runner` again. All previously passing tests must still pass. If regression detected, stop and fix before continuing.

### 5. Audit — Security Check (conditional)

If the task touches any of: authentication, authorization, database queries, file I/O, network calls, external APIs — invoke `security-auditor`.

- **Critical findings**: must be resolved before continuing to the next task.
- **High findings**: must be addressed before marking the task complete.
- **Medium/Informational**: document and continue.

### 6. Verify — Acceptance Criteria Check

Invoke `verifier` with the task's acceptance criteria. The verifier must return `Verified` for all criteria before proceeding.

### 7. Refactor — Clean the Implementation

Remove duplication, improve naming, simplify logic. Re-run tests after each refactor step to confirm the safety net holds.

### 8. Mark Complete

Update `docs/tasks-{feature}.md` — set the task status to `complete` with timestamp.

---

## Parallel Execution

Tasks with `parallel-safe: yes` and no unmet dependencies may be dispatched as background agents simultaneously. Merge results sequentially to avoid file conflicts.

## Stop Conditions

| Condition | Action |
|-----------|--------|
| Task fails `verifier` 3 times | Pause and report to user |
| `security-auditor` returns Critical finding | Stop all parallel work, address Critical first |
| An out-of-scope test starts failing after implementation | Stop and investigate before continuing |
| Dependency task is `failed` | Do not start dependent task; report to user |

## Progress Reporting

After each task completes, print a one-line summary:
```
[task-001] DONE — 3 tests passing, 0 security findings
[task-002] DONE — 5 tests passing, 1 High finding addressed
```

Report overall progress at the end:
```
Feature complete: {N}/{N} tasks done. Coverage: XX%. Open findings: 0 Critical, 0 High.
```
