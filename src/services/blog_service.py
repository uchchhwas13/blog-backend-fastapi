from src.repositories.blog_repository import BlogRepository
from src.models.blog import Blog
from src.models.user import User
from src.models.comment import Comment
from src.schemas.blog import AddBlogPostPayload, UpdateBlogPostPayload, BlogDetail, BlogItem, BlogModel, UserInfo, BlogWithCommentsResponse
from uuid import UUID
from src.schemas.blog import Comment as CommentSchema
from src.exceptions import AuthorizationError, ResourceNotFoundError, DatabaseError
from src.services.file_service import FileService
from src.schemas.pagination import PaginationMeta
from typing import Tuple


class BlogService:
    def __init__(self, blog_repo: BlogRepository):
        self.blog_repo = blog_repo
        self.file_service = FileService()

    async def add_blog_post(
        self,
        payload: AddBlogPostPayload,
        user: User
    ) -> BlogModel:
        try:
            new_blog = Blog(**payload.model_dump(), created_by=user.id)
            created_blog = await self.blog_repo.create(new_blog)

            return self._build_blog_model(created_blog, user)
        except Exception:
            raise DatabaseError("Failed to create blog post")

    async def update_blog_post(
        self,
        blog_id: str,
        payload: UpdateBlogPostPayload,
        user: User
    ) -> BlogModel:
        try:
            blog = await self._validate_blog_ownership(blog_id, user)
            old_image_url = blog.cover_image_url
            update_data = self._build_update_data(payload)
            updated_blog = await self._update_blog_record(blog_id, update_data)
            if payload.cover_image_url and old_image_url != payload.cover_image_url:
                await self.file_service.delete_file_if_exists(old_image_url)
            return self._build_blog_model(updated_blog, user)
        except ResourceNotFoundError:
            raise
        except AuthorizationError:
            raise
        except Exception:
            raise DatabaseError("Failed to update blog post")

    async def delete_blog_post(
        self,
        blog_id: str,
        user: User
    ) -> bool:
        try:
            blog = await self._validate_blog_ownership(blog_id, user)
            success = await self.blog_repo.delete_by_id(blog_id)
            if not success:
                raise ResourceNotFoundError("Blog", blog_id)
            await self.file_service.delete_file_if_exists(blog.cover_image_url)
            return True
        except ResourceNotFoundError:
            raise
        except AuthorizationError:
            raise
        except Exception:
            raise DatabaseError("Failed to delete blog post")

    async def _validate_blog_ownership(self, blog_id: str, user: User) -> Blog:
        blog = await self.blog_repo.get_by_id(blog_id)
        if not blog:
            raise ResourceNotFoundError("Blog", blog_id)
        if blog.created_by != user.id:
            raise AuthorizationError()
        return blog

    def _build_update_data(self, payload: UpdateBlogPostPayload) -> dict[str, str]:
        update_data: dict[str, str] = {}
        if payload.title is not None:
            update_data["title"] = payload.title
        if payload.body is not None:
            update_data["body"] = payload.body
        if payload.cover_image_url is not None:
            update_data["cover_image_url"] = payload.cover_image_url
        return update_data

    async def _update_blog_record(self, blog_id: str, update_data: dict[str, str]):
        updated_blog = await self.blog_repo.update_by_id(blog_id, update_data)
        if not updated_blog:
            raise ResourceNotFoundError("Blog", blog_id)
        return updated_blog

    def _build_blog_model(self, blog: Blog, user: User) -> BlogModel:
        return BlogModel(
            id=str(blog.id),
            title=blog.title,
            body=blog.body,
            cover_image_url=self.file_service.build_file_url(
                blog.cover_image_url),
            created_by=UserInfo(
                id=str(user.id),
                name=user.name,
                image_url=self.file_service.build_file_url(
                    user.profile_image_url)
            ),
            created_at=blog.created_at,
            updated_at=blog.updated_at
        )

    async def get_blog_list(
        self,
        page: int = 1,
        page_size: int = 9
    ) -> Tuple[list[BlogItem], PaginationMeta]:
        blogs, total_count = await self.blog_repo.get_paginated_blogs(page, page_size)

        total_pages = (total_count + page_size -
                       1) // page_size

        pagination_meta = PaginationMeta(
            current_page=page,
            page_size=page_size,
            total_items=total_count,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )

        blog_items = [
            BlogItem(
                id=blog.id,
                title=blog.title,
                cover_image_url=self.file_service.build_file_url(
                    blog.cover_image_url),
                created_at=blog.created_at
            )
            for blog in blogs
        ]

        return blog_items, pagination_meta

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
            cover_image_url=self.file_service.build_file_url(
                blog.cover_image_url),
            is_liked_by_user=is_liked_by_user,
            total_likes=blog.like_count,
            created_by=UserInfo(
                id=str(author.id),
                name=author.name,
                image_url=self.file_service.build_file_url(
                    author.profile_image_url),
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
                    image_url=self.file_service.build_file_url(
                        comment.author.profile_image_url),
                ),
                created_at=comment.created_at,
            )
            for comment in comments
        ]
