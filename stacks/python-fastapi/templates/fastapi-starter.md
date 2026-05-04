# FastAPI Project Scaffold

## Directory Structure
```
app/
  main.py                    # FastAPI app + lifespan + router registration
  core/
    config.py                # pydantic-settings Settings class
    database.py              # AsyncEngine + get_session() dependency
  modules/
    {feature}/
      routes.py              # @router.get/post/put/delete — HTTP only
      service.py             # async def business logic
      repository.py          # async def DB queries via SQLAlchemy
      models.py              # SQLAlchemy ORM models (snake_case)
      schemas.py             # Pydantic v2 request/response (CamelCase JSON)
tests/
  api/
    test_{feature}.py        # E2E tests via httpx.AsyncClient
  conftest.py                # async engine, db fixture, client fixture
alembic/
  env.py                     # async Alembic env
  versions/                  # migration files
Dockerfile
docker-compose.yml
pyproject.toml
.env.example
```

## Entry Point — app/main.py
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine
from app.modules.users.routes import router as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # startup: connection pool created by engine
    await engine.dispose()

app = FastAPI(title="{Project Name}", lifespan=lifespan)
app.include_router(users_router, prefix="/api/v1")
```

## Config — app/core/config.py
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/appdb"
    secret_key: str = "change-me"
    environment: str = "development"

settings = Settings()
```

## Database — app/core/database.py
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_session():
    async with SessionLocal() as session:
        yield session
```

## pyproject.toml
```toml
[project]
name = "{project-name}"
requires-python = ">=3.11"
dependencies = [
    "fastapi==0.111.0",
    "uvicorn[standard]==0.30.0",
    "sqlalchemy==2.0.31",
    "asyncpg==0.29.0",
    "alembic==1.13.2",
    "pydantic-settings==2.3.4",
    "pydantic[email]==2.8.2",
]

[project.optional-dependencies]
dev = [
    "pytest==8.2.2",
    "pytest-asyncio==0.23.7",
    "httpx==0.27.0",
    "anyio==4.4.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
```

## .env.example
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/appdb
SECRET_KEY=change-me-in-production
ENVIRONMENT=development
```

## Test Fixture — tests/conftest.py
See stacks/python-fastapi/templates/conftest.py for the full async test setup.
