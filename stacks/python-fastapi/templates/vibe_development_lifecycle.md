# FastAPI Development Lifecycle

This stack's git workflow and session structure follow the shared docs:
- Git branching, commits, PRs: see `stacks/shared/vibe_git_workflow.md`
- Session structure (start/work/end): see `stacks/shared/vibe_session_workflow.md`

---

## FastAPI-Specific Lifecycle Concerns

### Alembic Migration Discipline

- Never edit existing migrations. Always create a new one:
  ```bash
  alembic revision --autogenerate -m "{description}"
  ```
- Migration naming: `{timestamp}_{description}.py`. Description is snake_case imperative:
  `add_users_table`, `add_email_index`, `remove_deprecated_status_column`.
- Every PR that changes SQLAlchemy models must include an Alembic migration.
- `alembic upgrade head` runs in CI before the test suite.
- If autogenerate produces an empty migration, verify that your models are imported
  in the Alembic `env.py` target metadata.

### OpenAPI / Router Organization

- One router per resource (`users_router`, `orders_router`). Register all routers in `app/main.py`.
- Endpoint paths: `/users`, `/users/{user_id}`. No versioning prefix unless explicitly
  required — use `/v1/users` only when a `/v2/users` exists or is planned.
- Every endpoint must declare a `response_model`. No untyped dict responses.
- Deprecating an endpoint: add `deprecated=True` to the decorator. Do not remove the
  endpoint until the next major version.
- Tag routers with a resource name for clean OpenAPI docs:
  ```python
  router = APIRouter(prefix="/users", tags=["users"])
  ```

### Schema Migration Strategy

- Pydantic v2 model changes that break existing stored data require a migration path —
  do not silently change field types or remove fields without a plan.
- Use `model_config = ConfigDict(from_attributes=True)` on response schemas that
  read from ORM models.
- Keep request schemas (input) and response schemas (output) as separate Pydantic
  models even when they look similar. They evolve independently.
- Field validation belongs in the Pydantic model, not in the route handler or service.

### Async Discipline

- Use `async def` for all route handlers and service methods that perform I/O
  (database queries, HTTP calls, file reads).
- Never call a synchronous blocking function from an async context. Use
  `asyncio.run_in_executor` to wrap blocking calls, or replace with an async library.
- SQLAlchemy 2.0 async session pattern:
  ```python
  async with AsyncSession(engine) as session:
      async with session.begin():
          result = await session.execute(select(User).where(User.id == user_id))
  ```
- Never share a session across requests. Create a new session per request using
  FastAPI dependency injection.
- Do not use `session.commit()` inside route handlers — let the session context
  manager handle commit/rollback.

### Quality Gate (FastAPI)

The quality command for this stack is:

```bash
make quality
```

Which runs: `ruff check .`, `black --check .`, `mypy .`, `pytest`.

All four must pass before pushing. Address type errors — do not suppress them
with `# type: ignore` unless there is no alternative and the reason is documented.
