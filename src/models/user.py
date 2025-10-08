from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column, String
from sqlalchemy.sql import func
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .blog import Blog
    from .blog_like import BlogLike
    from .comment import Comment


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    email: str
    name: str
    profile_image_url: str = Field(
        default="/images/default.jpg",
        nullable=False
    )
    password_hash: str = Field(exclude=True)
    role: str = Field(sa_column=Column(
        pg.VARCHAR, nullable=False, server_default="user"
    ))
    refresh_token: Optional[str] = Field(
        sa_column=Column(String, nullable=True)
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
    blogs: list["Blog"] = Relationship(
        back_populates="author", sa_relationship_kwargs={"lazy": "selectin"})
    blog_likes: list["BlogLike"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    comments: list["Comment"] = Relationship(
        back_populates="author", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self) -> str:
        return f"<User {self.email}>"
