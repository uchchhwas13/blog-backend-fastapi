from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.blog import Blog
from src.models.user import User
from src.schemas.blog import AddBlogPostPayload, BlogModel, BlogCreatedBy


def build_file_url(path: str) -> str:
    base_url = "http://localhost:8000"
    return f"{base_url}{path}"


class BlogService:
    async def add_blog_post(self,
                            payload: AddBlogPostPayload,
                            user: User,
                            session: AsyncSession
                            ) -> BlogModel:

        new_blog = Blog(**payload.model_dump(),
                        created_by=user.id)
        new_blog.creator = user
        session.add(new_blog)
        await session.commit()

        return BlogModel(
            id=str(new_blog.id),
            title=new_blog.title,
            body=new_blog.body,
            cover_image_url=build_file_url(new_blog.cover_image_url),
            created_by=BlogCreatedBy(id=str(user.id), name=user.name),
            created_at=new_blog.created_at,
        )
