from typing import Generic, TypeVar
from pydantic import Field
from fastapi_camelcase import CamelModel

T = TypeVar('T')


class PaginationParams(CamelModel):
    """Query parameters for pagination"""
    page: int = Field(
        default=1, ge=1, description="Page number (starts from 1)")
    page_size: int = Field(default=9, ge=1, le=100,
                           description="Number of items per page")


class PaginationMeta(CamelModel):
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(CamelModel, Generic[T]):
    data: list[T]
    pagination: PaginationMeta
