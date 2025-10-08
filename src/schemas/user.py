from pydantic import Field, EmailStr
from datetime import datetime
import uuid

from fastapi_camelcase import CamelModel


class UserCreateModel(CamelModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    profile_image_url: str = Field(default="/images/default.jpg")
    role: str = "user"


class UserModel(CamelModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserLoginModel(CamelModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserResponse(CamelModel):
    email: EmailStr
    id: str
    name: str


class LoginResponse(CamelModel):
    access_token: str
    refresh_token: str
    user: UserResponse


class TokenPairResponse(CamelModel):
    access_token: str
    refresh_token: str


class TokenRefreshRequest(CamelModel):
    refresh_token: str


class LogOutResponse(CamelModel):
    message: str
    success: bool


class LogoutRequestModel(CamelModel):
    user_id: str
