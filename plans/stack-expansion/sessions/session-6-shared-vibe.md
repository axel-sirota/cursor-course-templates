# Session 6 — Shared Vibe Infrastructure

**Phase:** 2
**Parallel with:** Sessions 1–5 (touches only python-fastapi + creates new shared/ dir)
**Depends on:** nothing
**Next:** Sessions 7–12 (all new stacks reference shared/ docs)

## Goal
Extract the 90%-agnostic `vibe_development_lifecycle.md` from `python-fastapi` into a shared location. Create a truly language-agnostic session workflow doc. All new stacks (sessions 7–12) will reference these instead of duplicating content.

---

## Files to Create / Update

```
stacks/
└── shared/
    ├── README.md                           ← NEW (explains what shared/ is)
    ├── vibe_git_workflow.md                ← NEW (extracted from python-fastapi, Python-generic)
    └── vibe_session_workflow.md            ← NEW (fully language-agnostic)

stacks/python-fastapi/vibe/
└── vibe_development_lifecycle.md           ← UPDATE (thin wrapper → shared + FastAPI-specific additions)
```

---

## File Specifications

### `stacks/shared/README.md`

```markdown
# Shared Vibe Docs

These documents are shared across all stacks. They cover workflow patterns
that apply regardless of language, framework, or architecture shape.

- `vibe_git_workflow.md` — git branching, commit conventions, PR discipline (Python-oriented)
- `vibe_session_workflow.md` — AI session structure: start-session → work → next-session (language-agnostic)

Stack-specific vibe docs extend or override these for their language/toolchain.
```

### `stacks/shared/vibe_git_workflow.md`

Extracted and generalized from `python-fastapi/vibe/vibe_development_lifecycle.md`.

Sections to include (language-agnostic except tooling references):
- **Branch Strategy**: `main` (production), `develop` (integration), `feature/{name}` (work). PR from feature → develop. Merge develop → main on release.
- **Starting a feature**: `git checkout develop && git pull && git checkout -b feature/{name}`
- **Committing**: conventional commits format — `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`. Subject line ≤72 chars, imperative mood.
- **Pushing for review**: `git push origin feature/{name}` → open PR to develop.
- **PR description template**: Summary (what + why), Key Changes (bullet list), Testing (how it was tested), Screenshots if UI.
- **Merge discipline**: squash merge to keep history clean. Delete feature branch after merge.
- **Quality gate before push**: run your stack's quality command (`mvn verify`, `go test ./...`, `npm test`, `pytest`, etc.) — all green before pushing.
- **Hotfix flow**: branch from `main` → fix → PR to `main` AND `develop`.

### `stacks/shared/vibe_session_workflow.md`

Fully language-agnostic. Describes the AI session structure.

Sections:
- **What a session is**: a bounded unit of work with a defined goal, a defined start state, and a defined end state. Sessions prevent context drift.
- **Starting a session** (`/start-session`):
  1. Load context (persona + stack + active phase)
  2. Read last session's transition doc if present
  3. State the session goal explicitly before writing any code
  4. Confirm: goal fits within current active phase?
- **During a session**:
  - One thing at a time. Finish the current task before starting a new one.
  - Use subagents for isolated tasks (running tests, checking style, validating format).
  - Commit working checkpoints — don't accumulate hours of uncommitted work.
  - If you discover the goal is wrong, stop. Update the goal. Don't push forward on a wrong heading.
- **Ending a session** (`/next-session`):
  1. Run the quality gate (stack-specific)
  2. Commit everything with a meaningful commit message
  3. Write transition doc: what was accomplished, where you stopped, what's next, files to load in the next session
  4. Update `## Active Phase` in context if phase acceptance criteria are met
- **Transition doc format**:
  ```
  ## Session: {date} {goal}
  ### Accomplished
  - ...
  ### Stopped at
  {exact file and line or task}
  ### Next session
  {first action to take}
  ### Files to load
  - ...
  ```
- **Phase gates**: phases advance when ALL acceptance criteria are met, not when the developer is "mostly done." The AI must not advance a phase unilaterally — confirm with the user.

### `stacks/python-fastapi/vibe/vibe_development_lifecycle.md` (UPDATE)

Replace current content (which is 90% agnostic git workflow) with:

```markdown
# FastAPI Development Lifecycle

This stack's git workflow and session structure follow the shared docs:
- Git branching, commits, PRs: see `stacks/shared/vibe_git_workflow.md`
- Session structure (start/work/end): see `stacks/shared/vibe_session_workflow.md`

## FastAPI-Specific Lifecycle Concerns

### Alembic Migration Discipline
- Never edit existing migrations. Always `alembic revision --autogenerate -m "{description}"`.
- Migration naming: `{timestamp}_{description}.py`. Description is snake_case imperative: `add_users_table`, `add_email_index`.
- Every PR that changes models must include an Alembic migration.
- `alembic upgrade head` runs in CI before tests.

### OpenAPI / Router Organization
- One router per resource (`users_router`, `orders_router`). Register in `app/main.py`.
- Endpoint paths: `/users`, `/users/{user_id}`. No versioning prefix unless explicitly required (`/v1/users` only when you have a v2).
- Response models: every endpoint has a declared `response_model`. No untyped dict responses.
- Deprecating an endpoint: add `deprecated=True` to the decorator; don't remove until next major version.

### Schema Migration Strategy
- Pydantic v2 model changes that break existing data require a migration path.
- Use `model_config = ConfigDict(from_attributes=True)` on response schemas that read from ORM models.
- Keep request schema (what comes in) and response schema (what goes out) as separate Pydantic models even if they look similar.

### Async Discipline
- Use `async def` for all route handlers and service methods that do I/O.
- Never call a sync blocking function from an async context — use `asyncio.run_in_executor` or an async library.
- SQLAlchemy 2.0 async session: `async with AsyncSession(engine) as session:`. Never share session across requests.
```

---

## Acceptance Criteria

- [ ] `ls stacks/shared/` shows `README.md`, `vibe_git_workflow.md`, `vibe_session_workflow.md`
- [ ] `stacks/shared/vibe_session_workflow.md` contains zero language-specific references (no Python, Go, Java, Node)
- [ ] `stacks/shared/vibe_git_workflow.md` is derived from existing python-fastapi lifecycle doc — covers branch strategy, commit format, PR template, quality gate
- [ ] `stacks/python-fastapi/vibe/vibe_development_lifecycle.md` now contains FastAPI-specific content (Alembic, OpenAPI, async discipline) not present before
- [ ] `stacks/python-fastapi/vibe/vibe_development_lifecycle.md` references `stacks/shared/` docs
- [ ] No git workflow content duplicated between shared and fastapi docs
