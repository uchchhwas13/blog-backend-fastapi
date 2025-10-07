from typing import Optional, Annotated
from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .models.user import User
from src.services.auth_service import AuthService
from src.db.main import get_session
from .utils import verify_access_token
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession


class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        creds = await super().__call__(request)
        if creds is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated"
            )
        if not verify_access_token(creds.credentials):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired Token"
            )
        return creds


async def get_current_user_from_token(token_details: Annotated[HTTPAuthorizationCredentials, Depends(AccessTokenBearer())],
                                      session: AsyncSession = Depends(get_session)) -> Optional[User]:
    user_data = verify_access_token(token_details.credentials)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_email = user_data.get("user", {}).get("email")
    user = await AuthService().get_user_by_email(user_email, session)
    return user
