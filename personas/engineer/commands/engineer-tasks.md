# /engineer-tasks

Decompose an architect plan into parallel-safe tasks ready for `/engineer-implement`.

Paths are relative to `workspaces/engineer/`.

## Steps

1. **Locate the plan.** Read the current session file in `plans/sessions/` (the lowest-numbered one with unchecked tasks) and `plans/interface-contract.md`. A feature plan at `docs/plan-{feature}.md` also works. If several candidates exist, ask the user which one to use before proceeding.

2. **Identify task boundaries.** Split the plan into atomic tasks:
   - One task per API endpoint or function
   - One task per test file
   - One task per database migration
   - One task per major UI component

3. **Define each task** using this schema:
   ```
   id:           task-001 (sequential within feature)
   title:        Short imperative description
   acceptance:   Given / When / Then (three lines minimum)
   touched_files: list of files created or modified
   depends_on:   list of task ids (empty if none)
   ```

4. **Detect file conflicts.** Any two tasks that touch the same file must be marked `parallel-safe: no` and placed in sequential order. Tasks with no shared files and no unmet dependencies are `parallel-safe: yes`.

5. **Output `docs/tasks-{feature}.md`** with:
   - A summary table (id | title | depends_on | parallel-safe)
   - A detail section per task (acceptance criteria, touched files, suggested subagent for review)

## Output Format

```markdown
# Tasks: {feature}

## Summary

| id       | title                  | depends_on | parallel-safe |
|----------|------------------------|------------|---------------|
| task-001 | ...                    | none       | yes           |
| task-002 | ...                    | task-001   | no            |

## task-001: {title}

**Acceptance Criteria**
- Given: ...
- When: ...
- Then: ...

**Touched Files**
- `path/to/file.py`

**Review Agent**
- code-reviewer (always)
- security-auditor (if touches auth, DB, or external I/O)
```

## Notes

- Do not start implementation. This command produces the task file only.
- If `docs/` does not exist in the workspace, create it before writing the output file.
- If a plan references architecture diagrams or ADRs, reference them in the relevant task's detail section.
