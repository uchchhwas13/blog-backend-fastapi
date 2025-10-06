from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
import uuid


class UserCreateModel(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    profile_image: str = Field(default="/images/default.png")
    role: str = "user"


class UserModel(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
