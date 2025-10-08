from typing import Generic, TypeVar
from fastapi_camelcase import CamelModel

T = TypeVar("T")


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase"""
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def to_snake(string: str) -> str:
    """Convert camelCase to snake_case"""
    result = ""
    for char in string:
        if char.isupper():
            result += "_" + char.lower()
        else:
            result += char
    return result.lstrip("_")


class APIResponse(CamelModel, Generic[T]):
    data: T
    message: str
    success: bool
