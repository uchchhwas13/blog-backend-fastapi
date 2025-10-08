from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.models.blog import Blog
from src.models.user import User
from src.models.comment import Comment
from src.schemas.blog import AddBlogPostPayload, BlogDetail, BlogItem, BlogModel, AuthorInfo, BlogWithCommentsResponse
from uuid import UUID
from fastapi import HTTPException
from src.schemas.blog import Comment as CommentSchema, AuthorInfo
from sqlalchemy.orm import selectinload


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

    async def get_blog_details(
        self, blog_id: str, user_id: UUID | None, session: AsyncSession
    ) -> BlogWithCommentsResponse:
        blog = await self._fetch_blog_with_relationships(blog_id, session)
        is_liked_by_user = self._check_if_user_liked(blog, user_id)
        sanitized_blog = self._build_sanitized_blog(blog, is_liked_by_user)
        sanitized_comments = self._build_sanitized_comments(blog.comments)
        return BlogWithCommentsResponse(blog=sanitized_blog, comments=sanitized_comments)

    async def _fetch_blog_with_relationships(
        self, blog_id: str, session: AsyncSession
    ) -> Blog:
        statement = (
            select(Blog)
            .where(Blog.id == blog_id)
            .options(
                selectinload(Blog.author),
                selectinload(Blog.likes),
                selectinload(Blog.comments).selectinload(Comment.author),
            )
        )
        result = await session.exec(statement)
        blog = result.first()
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")
        return blog

    def _check_if_user_liked(self, blog: Blog, user_id: UUID | None) -> bool:
        if not user_id:
            return False
        return any(like.user_id == user_id for like in blog.likes)

    def _build_sanitized_blog(self, blog: Blog, is_liked_by_user: bool) -> BlogDetail:
        author = blog.author
        if not author:
            raise HTTPException(
                status_code=500, detail="Blog author not found")

        return BlogDetail(
            id=str(blog.id),
            title=blog.title,
            body=blog.body,
            cover_image_url=build_file_url(blog.cover_image_url),
            is_liked_by_user=is_liked_by_user,
            total_likes=blog.like_count,
            created_by=AuthorInfo(
                id=str(author.id),
                name=author.name,
                image_url=build_file_url(author.profile_image_url),
            ),
            created_at=blog.created_at,
        )

    def _build_sanitized_comments(self, comments: list[Comment]) -> list[CommentSchema]:
        sanitized_comments: list[CommentSchema] = []
        for comment in comments:
            author = comment.author
            sanitized_comments.append(
                CommentSchema(
                    id=str(comment.id),
                    content=comment.content,
                    created_by=AuthorInfo(
                        id=str(author.id),
                        name=author.name,
                        image_url=build_file_url(author.profile_image_url),
                    ),
                    created_at=comment.created_at,
                )
            )
        return sanitized_comments
