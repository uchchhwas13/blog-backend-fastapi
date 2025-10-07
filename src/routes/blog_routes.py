from typing import Annotated
from src.schemas.blog import AddBlogPostPayload, BlogListResponse
from src.services.blog_service import BlogService
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.dependencies import get_current_user_from_token
from src.models.user import User
from src.schemas.api_response import APIResponse
from src.schemas.blog import AddBlogPostPayload, BlogModel
import time
from pathlib import Path
from src.utils import validate_file

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

blog_router = APIRouter()
blog_service = BlogService()


async def blog_data_with_image(
    cover_image: UploadFile,
    title: str = Form(...),
    body: str = Form(...)
) -> AddBlogPostPayload:
    content = await cover_image.read()
    validate_file(cover_image, content)

    timestamp = int(time.time())
    file_name = f"{timestamp}-{cover_image.filename}"
    file_path = UPLOAD_DIR / file_name

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    image_path = f"/uploads/{file_name}"
    return AddBlogPostPayload(
        title=title,
        body=body,
        cover_image_url=image_path
    )


@blog_router.post("/", response_model=APIResponse[BlogModel], status_code=status.HTTP_201_CREATED)
async def add_blog_post(
    blog_data: AddBlogPostPayload = Depends(blog_data_with_image),
    current_user: User = Depends(get_current_user_from_token),
    session: AsyncSession = Depends(get_session),

):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = await blog_service.add_blog_post(blog_data, current_user, session)

    return APIResponse(data=data, success=True, message="Blog post created successfully")


@blog_router.get('/', response_model=APIResponse[BlogListResponse], status_code=status.HTTP_200_OK)
async def get_blog_list(session: Annotated[AsyncSession, Depends(get_session)]):
    blog_list = await blog_service.get_blog_list(session)
    return APIResponse(data=BlogListResponse(blogs=blog_list), success=True, message="Blog list fetched successfully")
