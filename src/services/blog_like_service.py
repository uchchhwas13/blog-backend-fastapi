from uuid import UUID
from sqlmodel import update
from sqlalchemy import func, cast, Boolean
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.repositories.blog_repository import BlogRepository
from src.repositories.blog_like_repository import BlogLikeRepository
from src.schemas.blog import UserInfo
from src.models.blog import Blog
from src.services.file_service import FileService


class BlogLikeService:
    def __init__(self, blog_repo: BlogRepository, blog_like_repo: BlogLikeRepository):
        self.blog_repo = blog_repo
        self.blog_like_repo = blog_like_repo

    async def update_like_status(
        self,
        blog_id: str,
        user_id: UUID,
        is_liked: bool,
        session: AsyncSession,
    ) -> bool:
        await self._ensure_blog_exists(blog_id)
        previous_is_liked = await self._get_previous_like_state(blog_id, user_id)

        if previous_is_liked == is_liked:
            return is_liked

        await self._upsert_blog_like(blog_id, user_id, is_liked)
        await self._update_blog_like_count(blog_id, is_liked, session)

        await session.commit()
        return is_liked

    async def _ensure_blog_exists(self, blog_id: str) -> None:
        exists = await self.blog_repo.exists(blog_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Blog not found")

    async def _get_previous_like_state(self, blog_id: str, user_id: UUID) -> bool:
        return await self.blog_like_repo.get_like_status(blog_id, user_id)

    async def _upsert_blog_like(
        self, blog_id: str, user_id: UUID, is_liked: bool
    ) -> None:
        await self.blog_like_repo.upsert(blog_id, user_id, is_liked)

    async def _update_blog_like_count(
        self, blog_id: str, is_liked: bool, session: AsyncSession
    ) -> None:
        delta = 1 if is_liked else -1
        await session.exec(
            update(Blog)
            .where(cast(Blog.id == blog_id, Boolean))
            .values(like_count=func.greatest(Blog.like_count + delta, 0))
        )

    async def get_total_likes(self, blog_id: str) -> list[UserInfo]:
        await self._ensure_blog_exists(blog_id)

        likes = await self.blog_like_repo.get_likes_for_blog(blog_id)

        users: list[UserInfo] = []
        for like in likes:
            user = like.user
            users.append(
                UserInfo(
                    id=str(user.id),
                    name=user.name,
                    image_url=FileService().build_file_url(user.profile_image_url)
                )
            )
        return users
