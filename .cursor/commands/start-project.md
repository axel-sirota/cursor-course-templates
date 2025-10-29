# Start Project Command

Initialize project-specific adaptations based on provided instructions (e.g., "blog", "inventory", "LLM-assisted app"). This command scaffolds domain guides in `vibe/`, adds useful templates in `templates/`, and suggests dependency updates (requirements) for FastAPI Python projects following TDD with pytest, ruff, and mypy.

## Purpose
- Adapt generic vibe rules and commands to a concrete project theme
- Generate domain patterns docs (DB, sessions, services, repositories)
- Optionally include LLM client usage patterns and templates

## Inputs
- Arguments: A short description of the project domain and optional features
  - Examples:
    - "blog"
    - "inventory management"
    - "chat app with LLM (OpenAI)"

## What This Command Does
1. Reads core guides to align with standards
   - @vibe/vibe_phase_workflow.md
   - @vibe/vibe_fastapi_boilerplate.md
   - @vibe/vibe_database.md
   - @vibe/vibe_development_lifecycle.md
2. Generates domain-focused guides in `vibe/`
3. Creates matching API/model templates in `templates/`
4. Suggests dependency entries for `requirements.txt` (no installs performed)
5. Provides next-step checklists for Architect Phase and Phase 0

## Generated Files

### 1) Vibe Domain Guide
- Path: `vibe/vibe_{domain}_guide.md`
- Content outline:
  - Domain overview (entities, basic workflows)
  - Data modeling tips (layered Pydantic models)
  - Repository/service patterns for the domain
  - Session management patterns (validation, auth hooks if needed)
  - Example endpoints and request/response shapes (camelCase JSON)
  - Testing strategy (E2E + unit with mocks)

### 2) Templates for the Domain
- Paths under `templates/`:
  - `templates/{domain}-models.md` – example layered Pydantic models
  - `templates/{domain}-repository.md` – SQLAlchemy repository patterns
  - `templates/{domain}-service.md` – service layer examples
  - `templates/{domain}-api.md` – FastAPI router examples
  - `templates/{domain}-tests.md` – pytest examples (E2E and unit)

### 3) Optional: LLM Integration Templates
If the input mentions an LLM:
- Add `templates/llm-client.md` with:
  - Minimal client setup (environment-based API key)
  - Usage patterns (request/response handling, timeouts, retries)
  - Abstractions for service layer to call the LLM client
  - Testing notes (mocking client responses)
- Add dependency suggestions to `requirements.txt` section:
  - For OpenAI-compatible SDKs: `openai>=1.0.0` or chosen vendor
  - HTTP client if needed: `httpx` (already recommended for tests)

## Suggested Requirements Additions (Manual)
- Always keep these core tools:
  - fastapi, uvicorn[standard]
  - pydantic[email], pydantic-settings
  - pytest, pytest-asyncio, pytest-cov, httpx
  - ruff, black, mypy, isort
- If DB is used (abstract Postgres):
  - sqlalchemy, alembic, psycopg[binary]
- If LLM is used:
  - openai (or specific LLM SDK)

## Execution Steps
1. Parse domain/features from arguments
2. Create `vibe/vibe_{domain}_guide.md` with domain-specific patterns
3. Create template files in `templates/` for models/repository/service/api/tests
4. If LLM mentioned, create `templates/llm-client.md` and add requirement notes
5. Print next-step checklist

## Next-Step Checklist
- Architect Phase
  - Adapt `openapi.yaml` using `templates/{domain}-api.md`
  - Write entities and operations in `plan/api-design/*.md`
- Phase 0 (Skeleton)
  - Implement routers with mock data per `templates/{domain}-api.md`
  - Ensure tests scaffold per `templates/{domain}-tests.md`
- Phase 1+
  - Implement DB models, repositories, services using provided templates
  - Follow TDD and pass E2E/unit tests

## Anti-Patterns to Avoid
- Hardcoding vendor-specific details in guides
- Mixing snake_case in API responses (use camelCase for JSON)
- Skipping tests in Phase 0 or implementation phases
- Adding dependencies without updating `requirements.txt`

## Usage Examples
```
@start-project blog
```
Generates blog domain guide and templates (posts, comments, users patterns).

```
@start-project "chat app with LLM (OpenAI)"
```
Generates chat domain guide and LLM client template with requirement notes.


