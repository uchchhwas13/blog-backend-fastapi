from typing import TypedDict
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import uuid
import jwt
from passlib.context import CryptContext
from .config import config
from pathlib import Path
from fastapi import UploadFile
from fastapi import HTTPException

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
    token: str = jwt.encode(
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )


def verify_refresh_token(token: str) -> Optional[dict[str, Any]]:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            key=config.JWT_REFRESH_TOKEN_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB


def validate_file(file: UploadFile, content: bytes) -> None:
    """Validate file type and size."""
    if not file.filename:
        return
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Max size allowed is 1MB"
        )
