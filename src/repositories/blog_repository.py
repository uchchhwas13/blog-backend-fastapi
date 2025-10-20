from typing import Optional, Tuple
from sqlmodel import select, desc, func
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

    async def get_paginated_blogs(
        self,
        page: int = 1,
        page_size: int = 9
    ) -> Tuple[list[Blog], int]:
        offset = (page - 1) * page_size

        # Get total count
        count_statement = select(func.count()).select_from(Blog)
        count_result = await self.session.exec(count_statement)
        total_count = count_result.one()

        # Get paginated blogs
        statement = (
            select(Blog)
            .order_by(desc(Blog.created_at))
            .offset(offset)
            .limit(page_size)
        )
        result = await self.session.exec(statement)
        blogs = list(result.all())
        return blogs, total_count

    async def get_by_id_with_relationships(self, blog_id: str) -> Optional[Blog]:
        return await self.get_by_id(blog_id)

    async def exists(self, blog_id: str) -> bool:
        blog = await self.get_by_id(blog_id)
        return blog is not None
