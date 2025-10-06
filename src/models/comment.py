from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy import func
import uuid


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )

    content: str = Field(nullable=False)

    created_by: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False
    )
    blog_id: uuid.UUID = Field(
        foreign_key="blogs.id",
        nullable=False
    )

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

    # Relationships
    creator: Optional["User"] = Relationship(back_populates="comments")
    blog: Optional["Blog"] = Relationship(back_populates="comments")
