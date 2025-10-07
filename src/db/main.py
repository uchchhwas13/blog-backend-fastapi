from collections.abc import AsyncGenerator
from src.config import config
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

# Import all models to ensure relationships are resolved
from src.models.user import User
from src.models.blog import Blog
from src.models.comment import Comment
from src.models.blog_like import BlogLike

async_engine = create_async_engine(
    config.DATABASE_URL)


async_session_maker = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
