"""Pydantic schemas for authentication endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    """Request model for user registration."""

    model_config = ConfigDict(populate_by_name=True)

    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    """Request model for user login."""

    model_config = ConfigDict(populate_by_name=True)

    email: str
    password: str


class AuthResponse(BaseModel):
    """Response model for authentication (register/login)."""

    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    token_type: str = Field(alias="tokenType", default="bearer")
    user_id: str = Field(alias="userId")
    username: str


class UserResponse(BaseModel):
    """Response model for user profile."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId")
    username: str
    email: str
    created_at: str = Field(alias="createdAt")
