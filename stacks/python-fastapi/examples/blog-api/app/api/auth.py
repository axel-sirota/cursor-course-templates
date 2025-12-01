"""
Authentication API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.database import get_db
from app.modules.users.services.user_service import UserService

router = APIRouter()


class RegisterRequest(BaseModel):
    """User registration request."""
    username: str
    password: str


class RegisterResponse(BaseModel):
    """User registration response."""
    userId: str
    username: str


class LoginRequest(BaseModel):
    """User login request."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """User login response."""
    userId: str
    username: str


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(request: RegisterRequest, conn = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        request: User registration details
        conn: Database connection
        
    Returns:
        RegisterResponse: Created user details
    """
    try:
        user_service = UserService(conn)
        user = user_service.create_user(request.username, request.password)
        
        return RegisterResponse(
            userId=str(user["id"]),
            username=user["username"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, conn = Depends(get_db)):
    """
    Login an existing user.
    
    Args:
        request: User login credentials
        conn: Database connection
        
    Returns:
        LoginResponse: User details
    """
    try:
        user_service = UserService(conn)
        user = user_service.authenticate_user(request.username, request.password)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return LoginResponse(
            userId=str(user["id"]),
            username=user["username"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
