from typing import Annotated
from src.exceptions import AuthenticationError
from src.services.file_service import FileService
from src.services.blog_like_service import BlogLikeService
from src.services.comment_service import CommentService
from src.schemas.blog import AddBlogPostPayload, UpdateBlogPostPayload, BlogLikeResponse, BlogListResponse, BlogResponse, BlogWithCommentsResponse, CommentPayload, CommentResponse, CommentCreateModel, LikePayload
from src.services.blog_service import BlogService
from fastapi import APIRouter, Depends, UploadFile, Form, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.dependencies.dependencies_auth import CurrentUserDep, OptionalCurrentUserDep
from src.dependencies.dependencies_repositories import BlogRepositoryDep, CommentRepositoryDep, BlogLikeRepositoryDep
from src.schemas.api_response import APIResponse
from src.schemas.blog import AddBlogPostPayload
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

blog_router = APIRouter()
file_service = FileService()


async def blog_data_with_image(
    cover_image: UploadFile = Form(..., alias="coverImage"),
    title: str = Form(...),
    body: str = Form(...)
) -> AddBlogPostPayload:
    image_path = await file_service.save_uploaded_file(file=cover_image)
    return AddBlogPostPayload(
        title=title,
        body=body,
        cover_image_url=image_path
    )

BlogDataDep = Annotated[AddBlogPostPayload, Depends(blog_data_with_image)]


async def update_blog_data(
    cover_image: UploadFile | None = Form(None, alias="coverImage"),
    title: str | None = Form(None),
    body: str | None = Form(None)
) -> UpdateBlogPostPayload:
    image_path = None
    if cover_image and cover_image.filename:
        image_path = await file_service.save_uploaded_file(file=cover_image)
    return UpdateBlogPostPayload(
        title=title,
        body=body,
        cover_image_url=image_path
    )

UpdateBlogDataDep = Annotated[UpdateBlogPostPayload, Depends(update_blog_data)]


@blog_router.post('', response_model=APIResponse[BlogResponse], status_code=status.HTTP_201_CREATED)
async def add_blog_post(
    blog_repo: BlogRepositoryDep,
    blog_data: BlogDataDep,
    current_user: CurrentUserDep,
):
    if not current_user:
        raise AuthenticationError()
    blog_service = BlogService(blog_repo)
    data = await blog_service.add_blog_post(blog_data, current_user)

    return APIResponse(data=BlogResponse(blog=data), success=True, message="Blog post created successfully")


@blog_router.patch('/{blog_id}', response_model=APIResponse[BlogResponse], status_code=status.HTTP_200_OK)
async def update_blog_post(
    blog_id: str,
    blog_repo: BlogRepositoryDep,
    blog_data: UpdateBlogDataDep,
    current_user: CurrentUserDep,
):
    if not current_user:
        raise AuthenticationError()
    blog_service = BlogService(blog_repo)
    data = await blog_service.update_blog_post(blog_id, blog_data, current_user)

    return APIResponse(data=BlogResponse(blog=data), success=True, message="Blog post updated successfully")


@blog_router.get('', response_model=APIResponse[BlogListResponse], status_code=status.HTTP_200_OK)
async def get_blog_list(blog_repo: BlogRepositoryDep):
    blog_service = BlogService(blog_repo)
    blog_list = await blog_service.get_blog_list()
    return APIResponse(data=BlogListResponse(blogs=blog_list), success=True, message="Blog list fetched successfully")


@blog_router.get('/{blog_id}', response_model=APIResponse[BlogWithCommentsResponse], status_code=status.HTTP_200_OK)
async def get_blog_details(
    blog_id: str,
    blog_repo: BlogRepositoryDep,
    current_user: OptionalCurrentUserDep
):
    blog_service = BlogService(blog_repo)
    user_id = current_user.id if current_user else None
    blog_details = await blog_service.get_blog_details(blog_id, user_id)

    return APIResponse(data=blog_details, success=True, message="Blog details fetched successfully")


@blog_router.post('/{blog_id}/comments', response_model=APIResponse[CommentResponse], status_code=status.HTTP_201_CREATED)
async def add_comment(
    blog_id: str,
    comment_data: CommentPayload,
    comment_repo: CommentRepositoryDep,
    current_user: CurrentUserDep
):
    comment_service = CommentService(comment_repo)
    model = CommentCreateModel(
        blog_id=blog_id, content=comment_data.content, created_by=current_user.id)
    comment = await comment_service.add_comment(model, current_user)

    return APIResponse(data=comment, success=True, message="Comment added successfully")


@blog_router.put('/{blog_id}/comments/{comment_id}', response_model=APIResponse[CommentResponse], status_code=status.HTTP_200_OK)
async def update_comment(
    blog_id: str,
    comment_id: str,
    comment_data: CommentPayload,
    comment_repo: CommentRepositoryDep,
    current_user: CurrentUserDep
):
    comment_service = CommentService(comment_repo)
    comment = await comment_service.update_comment(comment_id, comment_data.content, current_user)

    return APIResponse(data=comment, success=True, message="Comment updated successfully")


@blog_router.post('/{blog_id}/likes', response_model=APIResponse[LikePayload], status_code=status.HTTP_200_OK)
async def like_unlike_blog(
    blog_id: str,
    payload: LikePayload,
    session: Annotated[AsyncSession, Depends(get_session)],
    blog_repo: BlogRepositoryDep,
    blog_like_repo: BlogLikeRepositoryDep,
    current_user: CurrentUserDep
):
    blog_like_service = BlogLikeService(blog_repo, blog_like_repo)
    result = await blog_like_service.update_like_status(blog_id, current_user.id, payload.is_liked, session)

    return APIResponse(
        data=LikePayload(is_liked=result),
        success=True,
        message=f"Blog {'liked' if result else 'unliked'} successfully"
    )


@blog_router.get('/{blog_id}/likes', response_model=APIResponse[BlogLikeResponse], status_code=status.HTTP_200_OK)
async def get_blog_likes(
    blog_id: str,
    blog_repo: BlogRepositoryDep,
    blog_like_repo: BlogLikeRepositoryDep,
):
    blog_like_service = BlogLikeService(blog_repo, blog_like_repo)
    users = await blog_like_service.get_total_likes(blog_id)
    return APIResponse(
        data=BlogLikeResponse(total_likes=len(users), users=users),
        success=True,
        message="Total likes fetched successfully"
    )
