from typing import Optional
from src.repositories.user_repository import UserRepository
from src.models.user import User
from src.schemas.user import TokenPairResponse, UserCreateModel
from src.utils import create_access_token, create_refresh_token, generate_password_hash
from src.exceptions import (
    ResourceNotFoundError,
    DatabaseError,
    AuthorizationError
)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.user_repo.get_by_email(email)

    async def user_exists(self, email: str) -> bool:
        return await self.user_repo.email_exists(email)

    async def create_user(self, user_data: UserCreateModel) -> User:
        try:
            user_data_dict = user_data.model_dump()
            new_user = User(**user_data_dict)
            new_user.password_hash = generate_password_hash(user_data.password)
            return await self.user_repo.create(new_user)
        except Exception:
            raise DatabaseError("Failed to create user account")

    async def save_refresh_token(self, user: User, refresh_token: str) -> User:
        user.refresh_token = refresh_token
        return await self.user_repo.update(user)

    async def refresh_tokens(self, refresh_token: str, user_id: str) -> TokenPairResponse:
        try:
            user = await self.user_repo.get_by_id(user_id)

            if not user:
                raise ResourceNotFoundError("User", user_id)

            if user.refresh_token != refresh_token:
                raise AuthorizationError("Refresh token mismatch or invalid")

            new_refresh_token = create_refresh_token(user_data={
                'email': user.email,
                'user_id': str(user.id),
                'role': user.role
            })
            user.refresh_token = new_refresh_token
            new_access_token = create_access_token(user_data={
                'email': user.email,
                'user_id': str(user.id),
                'role': user.role
            })

            await self.user_repo.update(user)

            return TokenPairResponse(access_token=new_access_token, refresh_token=new_refresh_token)
        except (ResourceNotFoundError, AuthorizationError):
            raise
        except Exception:
            raise DatabaseError("Failed to refresh authentication tokens")

    async def remove_refresh_token(self, user_id: str) -> None:
        user = await self.get_user_by_id(user_id)
        if user:
            user.refresh_token = None
            await self.user_repo.update(user)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)
