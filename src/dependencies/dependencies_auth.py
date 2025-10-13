from typing import Optional, Annotated
from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.models.user import User
from src.services.auth_service import AuthService
from src.utils import verify_access_token
from fastapi.exceptions import HTTPException
from .dependencies_repositories import UserRepositoryDep


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


AccessTokenDep = Annotated[HTTPAuthorizationCredentials,
                           Depends(AccessTokenBearer())]


async def get_current_user_from_token(token_details: AccessTokenDep,
                                      user_repo: UserRepositoryDep
                                      ) -> Optional[User]:
    user_data = verify_access_token(token_details.credentials)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_email = user_data.get("user", {}).get("email")
    user = await AuthService(user_repo=user_repo).get_user_by_email(user_email)
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user_from_token)]


async def get_optional_current_user(
        user_repo: UserRepositoryDep,
    token_details: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False))
) -> Optional[User]:
    if not token_details:
        return None

    user_data = verify_access_token(token_details.credentials)
    if not user_data:
        return None

    user_email = user_data.get("user", {}).get("email")
    if not user_email:
        return None

    user = await AuthService(user_repo=user_repo).get_user_by_email(user_email)
    return user

OptionalCurrentUserDep = Annotated[Optional[User], Depends(
    get_optional_current_user)]
