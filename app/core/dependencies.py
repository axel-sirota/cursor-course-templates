"""FastAPI dependencies for authentication and database."""

from fastapi import Header, HTTPException, status


async def require_auth(authorization: str | None = Header(None)) -> dict[str, str]:
    """Mock authentication dependency - returns mock user data.
    
    In Phase 1, this will be replaced with real JWT token verification.
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        Dictionary with user_id and username
        
    Raises:
        HTTPException: 401 if authorization header is missing or invalid
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": "mock-user-123",
        "username": "mockuser",
    }
