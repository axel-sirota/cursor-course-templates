"""
Blog API - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api import auth, posts, comments

app = FastAPI(
    title="Blog API",
    description="Session-based FastAPI blog implementation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    init_db()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "blog-api"}

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/api/posts", tags=["Comments"])
