from src.repositories.blog_repository import BlogRepository
from src.models.blog import Blog
from src.models.user import User
from src.models.comment import Comment
from src.schemas.blog import AddBlogPostPayload, BlogDetail, BlogItem, BlogModel, UserInfo, BlogWithCommentsResponse
from uuid import UUID
from src.schemas.blog import Comment as CommentSchema
from src.utils import build_file_url
from src.exceptions import ResourceNotFoundError, DatabaseError


class BlogService:
    def __init__(self, blog_repo: BlogRepository):
        self.blog_repo = blog_repo

    async def add_blog_post(
        self,
        payload: AddBlogPostPayload,
        user: User
    ) -> BlogModel:
        try:
            new_blog = Blog(**payload.model_dump(), created_by=user.id)
            created_blog = await self.blog_repo.create(new_blog)

            return BlogModel(
                id=str(created_blog.id),
                title=created_blog.title,
                body=created_blog.body,
                cover_image_url=build_file_url(created_blog.cover_image_url),
                created_by=UserInfo(
                    id=str(user.id),
                    name=user.name,
                    image_url=build_file_url(user.profile_image_url)
                ),
                created_at=created_blog.created_at,
            )
        except Exception:
            raise DatabaseError("Failed to create blog post")

    async def get_blog_list(self) -> list[BlogItem]:
        blogs = await self.blog_repo.get_all_ordered_by_date()
        
        return [
            BlogItem(
                id=blog.id,
                title=blog.title,
                cover_image_url=build_file_url(blog.cover_image_url),
                created_at=blog.created_at
            )
            for blog in blogs
        ]

    async def get_blog_details(
        self, blog_id: str, user_id: UUID | None
    ) -> BlogWithCommentsResponse:
        blog = await self._fetch_blog_with_relationships(blog_id)
        is_liked_by_user = self._check_if_user_liked(blog, user_id)
        sanitized_blog = self._build_sanitized_blog(blog, is_liked_by_user)
        sanitized_comments = self._build_sanitized_comments(blog.comments)
        return BlogWithCommentsResponse(blog=sanitized_blog, comments=sanitized_comments)

    async def _fetch_blog_with_relationships(self, blog_id: str) -> Blog:
        try:
            blog = await self.blog_repo.get_by_id_with_relationships(blog_id)
            if not blog:
                raise ResourceNotFoundError("Blog", blog_id)
            return blog
        except ResourceNotFoundError:
            raise
        except Exception:
            raise DatabaseError("Failed to fetch blog details")

    def _check_if_user_liked(self, blog: Blog, user_id: UUID | None) -> bool:
        if not user_id:
            return False
        return any(like.user_id == user_id for like in blog.likes)

    def _build_sanitized_blog(self, blog: Blog, is_liked_by_user: bool) -> BlogDetail:
        author = blog.author

        return BlogDetail(
            id=str(blog.id),
            title=blog.title,
            body=blog.body,
            cover_image_url=build_file_url(blog.cover_image_url),
            is_liked_by_user=is_liked_by_user,
            total_likes=blog.like_count,
            created_by=UserInfo(
                id=str(author.id),
                name=author.name,
                image_url=build_file_url(author.profile_image_url),
            ),
            created_at=blog.created_at,
        )

    def _build_sanitized_comments(self, comments: list[Comment]) -> list[CommentSchema]:
        return [
            CommentSchema(
                id=str(comment.id),
                content=comment.content,
                created_by=UserInfo(
                    id=str(comment.author.id),
                    name=comment.author.name,
                    image_url=build_file_url(comment.author.profile_image_url),
                ),
                created_at=comment.created_at,
            )
            for comment in comments
        ]
