# Project Context: Python FastAPI

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy 2.0+ with AsyncIO)
- **Migrations**: Alembic
- **Testing**: Pytest (AsyncIO)
- **Linting**: Ruff
- **Formatting**: Black
- **Type Checking**: Mypy

## Vibe & Style
- **Coding Style**: Snake_case for variables/functions, PascalCase for classes.
- **Architecture**: Modular Monolith (`app/modules/`).
- **Pattern**: Repository Pattern + Service Layer.
- **Documentation**: Google-style docstrings.

## Key Rules
- **TDD**: Write E2E tests (`tests/api/`) BEFORE implementation.
- **Layered Models**: Use separate models for DB (`Snake_case`) and API (`CamelCase` JSON).
- **Dependency Injection**: Use FastAPI `Depends` for services and repos.
- **No Business Logic in Routes**: Routes only handle HTTP, delegate to Services.
- **Type Safety**: Full type hints required on all functions.

## Active Phase
- Current: Phase 0 (Skeleton)

