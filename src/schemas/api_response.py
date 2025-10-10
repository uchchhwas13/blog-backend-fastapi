from typing import Generic, TypeVar
from fastapi_camelcase import CamelModel

T = TypeVar("T")


class APIResponse(CamelModel, Generic[T]):
    data: T
    message: str
    success: bool
