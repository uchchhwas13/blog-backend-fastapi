from typing import TypedDict
from typing import Union
from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError as PydanticValidationError

from src.exceptions import BlogAPIException


async def blog_api_exception_handler(request: Request, exc: BlogAPIException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "error": {
                "code": exc.error_code,
                "details": exc.details
            }
        }
    )


class ValidationErrorField(TypedDict):
    field: str
    message: str
    type: str


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, PydanticValidationError]
) -> JSONResponse:
    errors: list[ValidationErrorField] = []

    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "success": False,
            "message": "Validation error",
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "details": {"fields": errors}
            }
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    error_id = id(exc)
    if isinstance(exc, IntegrityError):
        error_msg = "Database constraint violation. The operation conflicts with existing data."
        status_code = status.HTTP_409_CONFLICT
        error_code = "INTEGRITY_ERROR"
    else:
        error_msg = "A database error occurred. Please try again later."
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_code = "DATABASE_ERROR"

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": error_msg,
            "data": None,
            "error": {
                "code": error_code,
                "details": {"error_id": error_id}
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_id = id(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred. Please try again later.",
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "details": {"error_id": error_id}
            }
        }
    )


def register_exception_handlers(app: FastAPI) -> None:

    app.add_exception_handler(
        BlogAPIException, blog_api_exception_handler)  # type: ignore[misc]
    app.add_exception_handler(RequestValidationError,
                              # type: ignore[misc]
                              validation_exception_handler)

    app.add_exception_handler(PydanticValidationError,
                              # type: ignore[misc]
                              validation_exception_handler)
    app.add_exception_handler(
        SQLAlchemyError, sqlalchemy_exception_handler)  # type: ignore[misc]
    app.add_exception_handler(Exception, generic_exception_handler)
