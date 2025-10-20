from typing import Any, Optional


class BlogAPIException(Exception):

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(BlogAPIException):
    def __init__(self, message: str = "Authentication failed", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class InvalidCredentialsError(AuthenticationError):

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)


class TokenExpiredError(AuthenticationError):

    def __init__(self, token_type: str = "access"):
        super().__init__(f"{token_type.capitalize()} token has expired")


class InvalidTokenError(AuthenticationError):

    def __init__(self, token_type: str = "access"):
        super().__init__(f"Invalid {token_type} token")


class AuthorizationError(BlogAPIException):

    def __init__(self, message: str = "You are not authorized to perform this action"):
        super().__init__(message, status_code=403)


# Resource Exceptions
class ResourceNotFoundError(BlogAPIException):

    def __init__(self, resource_type: str, resource_id: Optional[str] = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(message, status_code=404)


# Validation Exceptions
class ValidationError(BlogAPIException):

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class FileValidationError(ValidationError):

    def __init__(self, message: str):
        super().__init__(message, details={"allowed_extensions": [
            "jpg", "jpeg", "png"], "max_size": "1MB"})


# Database Exceptions
class DatabaseError(BlogAPIException):

    def __init__(self, message: str = "Database operation failed", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)
