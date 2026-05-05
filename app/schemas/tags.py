"""Pydantic schemas for tag endpoints."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.posts import PostResponse


class TagResponse(BaseModel):
    """Response model for a tag."""

    model_config = ConfigDict(populate_by_name=True)

    tag_id: str = Field(alias="tagId")
    name: str
    post_count: int = Field(alias="postCount")


class TagPostsResponse(BaseModel):
    """Response model for posts filtered by tag."""

    model_config = ConfigDict(populate_by_name=True)

    tag: str
    posts: list[PostResponse]
    total: int
