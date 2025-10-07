from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy import func, UniqueConstraint
import uuid


class BlogLike(SQLModel, table=True):
    __tablename__ = "blog_likes"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    )

    blog_id: uuid.UUID = Field(
        foreign_key="blogs.id",
        nullable=False
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False
    )

    is_liked: bool = Field(default=False)

    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )
    )

    __table_args__ = (
        UniqueConstraint("blog_id", "user_id", name="uq_blog_user_like"),
    )

    # Relationships
    blog: "Blog" = Relationship(back_populates="likes")
    user: "User" = Relationship(back_populates="blog_likes")
