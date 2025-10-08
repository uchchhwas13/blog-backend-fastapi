from uuid import UUID
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import insert, update
from src.models.comment import Comment as CommentModel
from src.models.user import User
from src.schemas.blog import UserInfo, Comment, CommentResponse
from src.utils import build_file_url


class CommentService:
    async def add_comment(self,
                          blog_id: str,
                          content: str,
                          user: User,
                          session: AsyncSession,
                          ) -> CommentResponse:

        stmt = insert(CommentModel).values(
            content=content,
            blog_id=blog_id,
            created_by=user.id
        ).returning(CommentModel)
        result = await session.exec(stmt)
        await session.commit()
        response = self._to_comment_response(result.scalar_one(), user)
        return response

    async def update_comment(
        self,
        comment_id: str,
        new_content: str,
        user: User,
        session: AsyncSession,
    ) -> CommentResponse:

        stmt = (
            update(CommentModel)
            .where(CommentModel.id == UUID(comment_id))
            .values(content=new_content)
            .returning(CommentModel)
        )

        result = await session.exec(stmt)
        updated_comment = result.scalar_one_or_none()

        if updated_comment is None:
            raise HTTPException(status_code=404, detail="Comment not found")

        await session.commit()
        response = self._to_comment_response(updated_comment, user)
        return response

    def _to_comment_response(self, comment: CommentModel, author: User) -> CommentResponse:
        return CommentResponse(
            comment=Comment(
                id=str(comment.id),
                content=comment.content,
                created_by=UserInfo(
                    id=str(author.id),
                    name=author.name,
                    image_url=build_file_url(author.profile_image_url)
                ),
                created_at=comment.created_at
            )
        )
