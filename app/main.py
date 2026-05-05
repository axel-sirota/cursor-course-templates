"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, comments, health, posts, tags
from app.core.config import settings

app = FastAPI(
    title="Blog API",
    description="RESTful blog API with FastAPI, SQLAlchemy, and PostgreSQL",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(tags.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.
    
    Returns:
        Welcome message
    """
    return {
        "message": "Blog API - Visit /docs for interactive API documentation",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
    )
