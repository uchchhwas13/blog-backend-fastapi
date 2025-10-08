from datetime import datetime
from src.schemas.api_response import BaseCamelModel
import uuid


class AddBlogPostPayload(BaseCamelModel):
    title: str
    body: str
    cover_image_url: str


class UserInfo(BaseCamelModel):
    id: str
    name: str
    image_url: str


class BlogModel(BaseCamelModel):
    id: str
    title: str
    body: str
    cover_image_url: str
    created_by: UserInfo
    created_at: datetime


class BlogItem(BaseCamelModel):
    id: uuid.UUID
    title: str
    cover_image_url: str
    created_at: datetime


class BlogListResponse(BaseCamelModel):
    blogs: list[BlogItem]


class BlogDetail(BaseCamelModel):
    id: str
    title: str
    body: str
    cover_image_url: str
    is_liked_by_user: bool
    total_likes: int
    created_by: UserInfo
    created_at: datetime


class Comment(BaseCamelModel):
    id: str
    content: str
    created_by: UserInfo
    created_at: datetime


class BlogWithCommentsResponse(BaseCamelModel):
    blog: BlogDetail
    comments: list[Comment]


class CommentPayload(BaseCamelModel):
    content: str


class CommentResponse(BaseCamelModel):
    comment: Comment


class LikePayload(BaseCamelModel):
    is_liked: bool


class BlogLikeResponse(BaseCamelModel):
    total_likes: int
    users: list[UserInfo]
