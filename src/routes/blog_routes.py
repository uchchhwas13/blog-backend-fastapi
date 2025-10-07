from src.schemas.blog import AddBlogPostPayload
from src.services.blog_service import BlogService
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.dependencies import get_current_user_from_token
from src.models.user import User
from src.schemas.api_response import APIResponse
from src.schemas.blog import AddBlogPostPayload, BlogModel
from typing import Annotated

blog_router = APIRouter()
blog_service = BlogService()


@blog_router.post("/", response_model=APIResponse[BlogModel], status_code=status.HTTP_201_CREATED)
async def handle_add_blog_post(
    title: str = Form(...),
    body: str = Form(...),
    cover_image: UploadFile = File(...),
    current_user: User = Depends(get_current_user_from_token),
    session: AsyncSession = Depends(get_session),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not cover_image:
        raise HTTPException(status_code=400, detail="File upload failed")

    blog_data = AddBlogPostPayload(title=title, body=body)
    data = await blog_service.add_blog_post(blog_data, current_user, cover_image, session)

    return APIResponse(data=data, success=True, message="Blog post created successfully")
