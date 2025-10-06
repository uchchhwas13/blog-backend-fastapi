from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, Column
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import func
import uuid


class Blog(SQLModel, table=True):
    __tablename__ = "blogs"

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
    creator: Optional["User"] = Relationship(back_populates="blogs")
    likes: list["BlogLike"] = Relationship(back_populates="blogs")
