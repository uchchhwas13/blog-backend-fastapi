from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.comment import Comment
from .base import BaseRepository


class CommentRepository(BaseRepository[Comment]):

    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)
