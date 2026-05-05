"""Pydantic schemas for post endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class CreatePostRequest(BaseModel):
    """Request model for creating a post."""

    model_config = ConfigDict(populate_by_name=True)

    title: str
    content: str
    tags: list[str] | None = None
    published: bool = True


class UpdatePostRequest(BaseModel):
    """Request model for updating a post."""

    model_config = ConfigDict(populate_by_name=True)

    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    published: bool | None = None


class PostResponse(BaseModel):
    """Response model for a single post."""

    model_config = ConfigDict(populate_by_name=True)

    post_id: str = Field(alias="postId")
    title: str
    content: str
    author_id: str = Field(alias="authorId")
    author_username: str = Field(alias="authorUsername")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    published: bool
    tags: list[str] = Field(default_factory=list)


class PostListResponse(BaseModel):
    """Response model for paginated list of posts."""

    model_config = ConfigDict(populate_by_name=True)

    posts: list[PostResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")
