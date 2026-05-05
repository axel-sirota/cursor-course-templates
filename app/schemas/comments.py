"""Pydantic schemas for comment endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class CreateCommentRequest(BaseModel):
    """Request model for creating a comment."""

    model_config = ConfigDict(populate_by_name=True)

    content: str


class CommentResponse(BaseModel):
    """Response model for a comment."""

    model_config = ConfigDict(populate_by_name=True)

    comment_id: str = Field(alias="commentId")
    post_id: str = Field(alias="postId")
    author_id: str = Field(alias="authorId")
    author_username: str = Field(alias="authorUsername")
    content: str
    created_at: str = Field(alias="createdAt")
