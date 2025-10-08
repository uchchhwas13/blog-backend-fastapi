from uuid import UUID, uuid4
from sqlmodel import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.blog import Blog
from src.models.blog_like import BlogLike


class BlogLikeService:
    async def update_like_status(
        self,
        blog_id: str,
        user_id: UUID,
        is_liked: bool,
        session: AsyncSession,
    ) -> bool:
        # 1️⃣ Ensure the blog exists
        blog = (await session.exec(select(Blog).where(Blog.id == blog_id))).first()
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        # 2️⃣ Get previous like state (if exists)
        stmt = select(BlogLike.is_liked).where(
            (BlogLike.blog_id == blog_id) &
            (BlogLike.user_id == user_id)
        )
        result = await session.exec(stmt)
        previous_is_liked = result.first() or False

        # 3️⃣ If state didn’t change, do nothing
        if previous_is_liked == is_liked:
            return is_liked

        # 4️⃣ Upsert (insert or update existing)
        stmt = (
            insert(BlogLike)
            .values(
                id=uuid4(),
                blog_id=blog_id,
                user_id=user_id,
                is_liked=is_liked
            )
            .on_conflict_do_update(
                index_elements=[BlogLike.blog_id, BlogLike.user_id],
                set_={
                    "is_liked": is_liked,
                    "updated_at": func.now()
                },
            )
        )
        await session.exec(stmt)

        # 5️⃣ Compute delta (+1 or -1)
        delta = 1 if is_liked else -1

        # 6️⃣ Update blog’s like_count safely
        await session.exec(
            update(Blog)
            .where(Blog.id == blog_id)
            .values(like_count=func.greatest(Blog.like_count + delta, 0))
        )

        await session.commit()

        return is_liked
