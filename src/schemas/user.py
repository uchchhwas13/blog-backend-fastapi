from pydantic import BaseModel, Field, EmailStr


class UserCreateModel(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    profile_image: str | None = None
