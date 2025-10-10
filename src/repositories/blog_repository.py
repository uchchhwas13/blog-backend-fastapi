"""
Blog repository for blog-specific database operations.
"""

from typing import Optional
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.blog import Blog
from .base import BaseRepository


class BlogRepository(BaseRepository[Blog]):

    def __init__(self, session: AsyncSession):
        super().__init__(Blog, session)

    async def get_all_ordered_by_date(self) -> list[Blog]:
        statement = select(Blog).order_by(desc(Blog.created_at))
        result = await self.session.exec(statement)
        return list(result.all())

    async def get_by_id_with_relationships(self, blog_id: str) -> Optional[Blog]:
        return await self.get_by_id(blog_id)

    async def exists(self, blog_id: str) -> bool:
        blog = await self.get_by_id(blog_id)
        return blog is not None
