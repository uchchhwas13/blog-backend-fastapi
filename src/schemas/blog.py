from pydantic import BaseModel
from datetime import datetime


class AddBlogPostPayload(BaseModel):
    title: str
    body: str
    cover_image_url: str


class BlogCreatedBy(BaseModel):
    id: str
    name: str


class BlogModel(BaseModel):
    id: str
    title: str
    body: str
    cover_image_url: str
    created_by: BlogCreatedBy
    created_at: datetime
