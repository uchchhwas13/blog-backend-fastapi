from pydantic import Field, EmailStr
from datetime import datetime
import uuid

from src.schemas.api_response import BaseCamelModel


class UserCreateModel(BaseCamelModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    profile_image: str = Field(default="/images/default.png")
    role: str = "user"


class UserModel(BaseCamelModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserLoginModel(BaseCamelModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserResponse(BaseCamelModel):
    email: EmailStr
    id: str
    name: str


class LoginResponse(BaseCamelModel):
    access_token: str
    refresh_token: str
    user: UserResponse


class TokenPairResponse(BaseCamelModel):
    access_token: str
    refresh_token: str


class TokenRefreshRequest(BaseCamelModel):
    refresh_token: str


class LogOutResponse(BaseCamelModel):
    message: str
    success: bool


class LogoutRequestModel(BaseCamelModel):
    user_id: str
