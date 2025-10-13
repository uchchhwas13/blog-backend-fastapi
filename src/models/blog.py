from datetime import datetime
from sqlmodel import Field, Relationship, Column
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import func
import uuid
from .base_model import BaseModel

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .user import User
    from .comment import Comment
    from .blog_like import BlogLike


class Blog(BaseModel, table=True):
    __tablename__ = "blogs"  # type: ignore[arg-type]

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    title: str = Field(nullable=False)
    body: str = Field(nullable=False)
    cover_image_url: str = Field(nullable=False)

    like_count: int = Field(
        default=0,
        nullable=False
    )

    created_by: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False
    )

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True),
                         server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        )
    )

    # Relationships
    author: "User" = Relationship(
        back_populates="blogs", sa_relationship_kwargs={"lazy": "selectin"})
    likes: list["BlogLike"] = Relationship(
        back_populates="blog", sa_relationship_kwargs={"lazy": "selectin"})
    comments: list["Comment"] = Relationship(
        back_populates="blog", sa_relationship_kwargs={"lazy": "selectin"})
