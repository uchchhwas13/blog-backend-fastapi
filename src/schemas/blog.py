from datetime import datetime
from src.schemas.api_response import BaseCamelModel
import uuid


class AddBlogPostPayload(BaseCamelModel):
    title: str
    body: str
    cover_image_url: str


class BlogCreatedBy(BaseCamelModel):
    id: str
    name: str


class BlogModel(BaseCamelModel):
    id: str
    title: str
    body: str
    cover_image_url: str
    created_by: BlogCreatedBy
    created_at: datetime


class BlogItem(BaseCamelModel):
    id: uuid.UUID
    title: str
    cover_image_url: str
    created_at: datetime


class BlogListResponse(BaseCamelModel):
    blogs: list[BlogItem]
