
from typing import List
from uuid import UUID, uuid4
from sqlmodel import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.blog_like import BlogLike
from .base import BaseRepository


class BlogLikeRepository(BaseRepository[BlogLike]):

    def __init__(self, session: AsyncSession):
        super().__init__(BlogLike, session)

    async def get_like_status(self, blog_id: str, user_id: UUID) -> bool:
        stmt = select(BlogLike.is_liked).where(
            (BlogLike.blog_id == blog_id) & (BlogLike.user_id == user_id)
        )
        result = await self.session.exec(stmt)
        return result.first() or False

    async def upsert(self, blog_id: str, user_id: UUID, is_liked: bool) -> None:
        stmt = (
            pg_insert(BlogLike)
            .values(
                id=uuid4(),
                blog_id=blog_id,
                user_id=user_id,
                is_liked=is_liked
            )
            .on_conflict_do_update(
                index_elements=["blog_id", "user_id"],
                set_={"is_liked": is_liked, "updated_at": func.now()},
            )
        )
        await self.session.exec(stmt)
        await self.session.commit()

    async def get_likes_for_blog(self, blog_id: str) -> List[BlogLike]:
        statement = select(BlogLike).where(
            (BlogLike.blog_id == blog_id) & (BlogLike.is_liked == True)
        )
        result = await self.session.exec(statement)
        return list(result.all())
