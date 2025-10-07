from pydantic import BaseModel
from typing import Generic, TypeVar, Any, Dict, Union, Type

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


class BaseCamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
        by_alias = True  # This ensures output uses camelCase aliases

    @classmethod
    def model_validate(cls: Type["BaseCamelModel"], obj: Union[Dict[str, Any], Any], **kwargs: Any) -> "BaseCamelModel":
        if isinstance(obj, dict):
            converted: Dict[str, Any] = {}
            for k, v in obj.items():
                if isinstance(k, str):
                    converted[to_snake(k)] = v
                else:
                    converted[str(k)] = v
            obj = converted
        return super().model_validate(obj, **kwargs)


class APIResponse(BaseCamelModel, Generic[T]):
    data: T
    message: str
    success: bool
