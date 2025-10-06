from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column, String
from sqlalchemy.sql import func
import uuid


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
        default="/images/default.png",
        nullable=False
    )
    password_hash: str = Field(exclude=True)
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

    def __repr__(self) -> str:
        return f"<User {self.email}>"
