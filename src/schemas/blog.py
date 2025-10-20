from src.schemas.pagination import PaginationMeta
from datetime import datetime
from fastapi_camelcase import CamelModel
import uuid


class AddBlogPostPayload(CamelModel):
    title: str
    body: str
    cover_image_url: str


class UpdateBlogPostPayload(CamelModel):
    title: str | None = None
    body: str | None = None
    cover_image_url: str | None = None


class UserInfo(CamelModel):
    id: str
    name: str
    image_url: str


class BlogModel(CamelModel):
    id: str
    title: str
    body: str
    cover_image_url: str
    created_by: UserInfo
    created_at: datetime
    updated_at: datetime


class BlogResponse(CamelModel):
    blog: BlogModel


class BlogItem(CamelModel):
    id: uuid.UUID
    title: str
    cover_image_url: str
    created_at: datetime


class BlogListResponse(CamelModel):
    blogs: list[BlogItem]
    pagination: PaginationMeta


class BlogDetail(CamelModel):
    id: str
    title: str
    body: str
    cover_image_url: str
    is_liked_by_user: bool
    total_likes: int
    created_by: UserInfo
    created_at: datetime


class Comment(CamelModel):
    id: str
    content: str
    created_by: UserInfo
    created_at: datetime


class BlogWithCommentsResponse(CamelModel):
    blog: BlogDetail
    comments: list[Comment]


class CommentPayload(CamelModel):
    content: str


class CommentCreateModel(CamelModel):
    blog_id: str
    content: str
    created_by: uuid.UUID


class CommentResponse(CamelModel):
    comment: Comment


class LikePayload(CamelModel):
    is_liked: bool


class BlogLikeResponse(CamelModel):
    total_likes: int
    users: list[UserInfo]
