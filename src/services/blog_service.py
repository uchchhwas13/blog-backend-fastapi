from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.models.blog import Blog
from src.models.user import User
from src.models.comment import Comment
from src.schemas.blog import AddBlogPostPayload, BlogDetail, BlogItem, BlogModel, AuthorInfo, BlogWithCommentsData
from uuid import UUID
from fastapi import HTTPException
from src.schemas.blog import Comment as CommentSchema, AuthorInfo


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
        session.add(new_blog)
        await session.commit()
        await session.refresh(new_blog)

        return BlogModel(
            id=str(new_blog.id),
            title=new_blog.title,
            body=new_blog.body,
            cover_image_url=build_file_url(new_blog.cover_image_url),
            created_by=AuthorInfo(
                id=str(user.id),
                name=user.name,
                image_url=build_file_url(user.profile_image_url)
            ),
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

    async def get_blog_details(self, blog_id: str, user_id: UUID | None, session: AsyncSession) -> BlogWithCommentsData:
        # 1. Fetch blog with relationships
        from sqlalchemy.orm import selectinload
        statement = select(Blog).where(Blog.id == blog_id).options(
            selectinload(Blog.author),
            selectinload(Blog.likes),
            selectinload(Blog.comments).selectinload(Comment.author)
        )
        blog_result = await session.exec(statement)
        blog = blog_result.first()

        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        # 2. Check if user liked this blog
        is_liked_by_user = False
        if user_id:
            for like in blog.likes:
                if like.user_id == user_id:
                    is_liked_by_user = True
                    break

        # 3. Build sanitized blog response
        author = blog.author
        if not author:
            raise HTTPException(
                status_code=500, detail="Blog author not found")

        sanitized_blog = BlogDetail(
            id=str(blog.id),
            title=blog.title,
            body=blog.body,
            cover_image_url=build_file_url(blog.cover_image_url),
            is_liked_by_user=is_liked_by_user,
            total_likes=blog.like_count,
            created_by=AuthorInfo(
                id=str(author.id),
                name=author.name,
                image_url=build_file_url(author.profile_image_url)
            ),
            created_at=blog.created_at,
        )

        # 4. Build comments
        sanitized_comments: list[CommentSchema] = []
        for comment in blog.comments:
            sanitized_comments.append(
                CommentSchema(
                    id=str(comment.id),
                    content=comment.content,
                    created_by=AuthorInfo(
                        id=str(comment.author.id),
                        name=comment.author.name,
                        image_url=build_file_url(
                            comment.author.profile_image_url),
                    ),
                    created_at=comment.created_at,
                )
            )

        return BlogWithCommentsData(blog=sanitized_blog, comments=sanitized_comments)
