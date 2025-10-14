from typing import TypedDict
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import uuid
import jwt
from passlib.context import CryptContext
from .config import config
from src.exceptions import (
    TokenExpiredError,
    InvalidTokenError,
)

password_context = CryptContext(schemes=["bcrypt"])
ACCESS_TOKEN_EXPIRY_DURATION = 300
REFRESH_TOKEN_EXPIRY_DURATION = 3600


class UserDataDict(TypedDict):
    email: str
    user_id: str
    role: str


def generate_password_hash(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)


def create_access_token(user_data: UserDataDict) -> str:
    payload: dict[str, Any] = {
        "user": user_data,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_EXPIRY_DURATION),
        "type": "access",
        "jti": str(uuid.uuid4())
    }

    token = jwt.encode(
        payload,
        key=config.JWT_ACCESS_TOKEN_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM,
    )
    return token


def create_refresh_token(user_data: UserDataDict) -> str:
    payload: dict[str, Any] = {
        "user": user_data,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=REFRESH_TOKEN_EXPIRY_DURATION),
        "type": "refresh",
        "jti": str(uuid.uuid4())
    }
    token = jwt.encode(
        payload,
        key=config.JWT_REFRESH_TOKEN_SECRET_KEY,
        algorithm=config.JWT_ALGORITHM,
    )
    return token


def verify_access_token(token: str) -> Optional[dict[str, Any]]:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            key=config.JWT_ACCESS_TOKEN_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            raise InvalidTokenError(token_type="access")
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError(token_type="access")
    except jwt.PyJWTError:
        raise InvalidTokenError(token_type="access")


def verify_refresh_token(token: str) -> Optional[dict[str, Any]]:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            key=config.JWT_REFRESH_TOKEN_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise InvalidTokenError(token_type="refresh")
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError(token_type="refresh")
    except jwt.PyJWTError:
        raise InvalidTokenError(token_type="refresh")
