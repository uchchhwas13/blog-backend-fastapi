from typing import Annotated
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.repositories.user_repository import UserRepository
from src.repositories.blog_repository import BlogRepository
from src.repositories.comment_repository import CommentRepository
from src.repositories.blog_like_repository import BlogLikeRepository


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepository:
    return UserRepository(session)


def get_blog_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> BlogRepository:
    return BlogRepository(session)


def get_comment_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> CommentRepository:
    return CommentRepository(session)


def get_blog_like_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> BlogLikeRepository:
    return BlogLikeRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
BlogRepositoryDep = Annotated[BlogRepository, Depends(get_blog_repository)]
CommentRepositoryDep = Annotated[CommentRepository, Depends(
    get_comment_repository)]
BlogLikeRepositoryDep = Annotated[BlogLikeRepository, Depends(
    get_blog_like_repository)]
