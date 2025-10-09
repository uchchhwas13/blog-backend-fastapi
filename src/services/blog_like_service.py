from uuid import UUID, uuid4
from sqlmodel import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schemas.blog import UserInfo
from src.models.blog import Blog
from src.models.blog_like import BlogLike

from src.utils import build_file_url


class BlogLikeService:

    async def update_like_status(
        self,
        blog_id: str,
        user_id: UUID,
        is_liked: bool,
        session: AsyncSession,
    ) -> bool:
        await self._ensure_blog_exists(blog_id, session)
        previous_is_liked = await self._get_previous_like_state(blog_id, user_id, session)

        if previous_is_liked == is_liked:
            return is_liked

        await self._upsert_blog_like(blog_id, user_id, is_liked, session)
        await self._update_blog_like_count(blog_id, is_liked, session)

        await session.commit()
        return is_liked

    async def _ensure_blog_exists(self, blog_id: str, session: AsyncSession) -> None:
        blog = (await session.exec(select(Blog).where(Blog.id == blog_id))).first()
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

    async def _get_previous_like_state(
        self, blog_id: str, user_id: UUID, session: AsyncSession
    ) -> bool:
        stmt = select(BlogLike.is_liked).where(
            (BlogLike.blog_id == blog_id) & (BlogLike.user_id == user_id)
        )
        result = await session.exec(stmt)
        return result.first() or False

    async def _upsert_blog_like(
        self, blog_id: str, user_id: UUID, is_liked: bool, session: AsyncSession
    ) -> None:
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
        await session.exec(stmt)

    async def _update_blog_like_count(
        self, blog_id: str, is_liked: bool, session: AsyncSession
    ) -> None:
        delta = 1 if is_liked else -1
        await session.exec(
            update(Blog)
            .where(Blog.id == blog_id)
            .values(like_count=func.greatest(Blog.like_count + delta, 0))
        )

    async def get_total_likes(
        self,
        blog_id: str,
        session: AsyncSession
    ) -> list[UserInfo]:
        await self._ensure_blog_exists(blog_id, session)

        stmt = select(BlogLike).where(
            (BlogLike.blog_id == blog_id) & (BlogLike.is_liked == True)
        )

        result = await session.exec(stmt)
        likes = result.all()

        users: list[UserInfo] = []
        for like in likes:
            user = like.user
            if not user:
                continue
            users.append(
                UserInfo(
                    id=str(user.id),
                    name=user.name,
                    image_url=build_file_url(
                        user.profile_image_url)
                )
            )
        return users
