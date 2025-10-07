from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.models.blog import Blog
from src.models.user import User
from src.schemas.blog import AddBlogPostPayload, BlogItem, BlogModel, AuthorInfo


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
            created_by=AuthorInfo(id=str(user.id), name=user.name),
            created_at=new_blog.created_at,
        )

    async def get_blog_list(self, session: AsyncSession) -> list[BlogItem]:
        statement = select(Blog).order_by(desc(Blog.created_at))
        result = await session.exec(statement)
        blog_items = list(
            map(
                lambda blog: BlogItem(
                    id=blog.id,
                    title=blog.title,
                    cover_image_url=build_file_url(blog.cover_image_url),
                    created_at=blog.created_at
                ),
                result
            )
        )
        return blog_items
