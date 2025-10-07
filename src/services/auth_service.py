from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User
from ..models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from ..schemas.user import TokenPairResponse, UserCreateModel
from ..utils import create_access_token, create_refresh_token, generate_password_hash


class AuthService:
    async def get_user_by_email(self, email: str, session: AsyncSession) -> Optional[User]:
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        user = result.first()
        return user

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession) -> User:
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(user_data.password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    async def save_refresh_token(self, user: User, refresh_token: str, session: AsyncSession) -> User:
        user.refresh_token = refresh_token
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def refresh_tokens(self,  refresh_token: str, user_id: str, session: AsyncSession) -> TokenPairResponse:

        result = await session.exec(select(User).where(User.id == user_id))
        user = result.first()

        if not user or user.refresh_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token mismatch or invalid"
            )

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

        session.add(user)
        await session.commit()

        return TokenPairResponse(access_token=new_access_token, refresh_token=new_refresh_token)
