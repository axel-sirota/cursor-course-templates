"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Dictionary with status "ok"
    """
    return {"status": "ok"}
