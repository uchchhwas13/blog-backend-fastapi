from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        result = await self.session.exec(statement)
        return result.first()

    async def email_exists(self, email: str) -> bool:
        user = await self.get_by_email(email)
        return user is not None
