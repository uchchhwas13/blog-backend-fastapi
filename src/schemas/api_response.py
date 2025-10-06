from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    data: T
    message: str
    success: bool
