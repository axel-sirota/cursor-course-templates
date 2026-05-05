"""Authentication endpoints - MOCK IMPLEMENTATION.

Phase 0: Returns hardcoded mock responses.
Phase 1: Will implement real authentication with database and JWT.
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import require_auth
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(request: RegisterRequest) -> AuthResponse:
    """Register a new user - MOCK IMPLEMENTATION.
    
    Args:
        request: Registration details (username, email, password)
        
    Returns:
        Mock authentication response with token
    """
    return AuthResponse(
        access_token="mock-jwt-token-" + request.username,
        token_type="bearer",
        user_id="mock-user-123",
        username=request.username,
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    """Login with email and password - MOCK IMPLEMENTATION.
    
    Args:
        request: Login credentials (email, password)
        
    Returns:
        Mock authentication response with token
    """
    return AuthResponse(
        access_token="mock-jwt-token-" + request.email,
        token_type="bearer",
        user_id="mock-user-123",
        username="mockuser",
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: dict[str, str] = Depends(require_auth)) -> UserResponse:
    """Get current authenticated user profile - MOCK IMPLEMENTATION.
    
    Args:
        current_user: Current user from auth dependency
        
    Returns:
        Mock user profile
    """
    return UserResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        email="mockuser@example.com",
        created_at="2024-01-01T00:00:00Z",
    )
