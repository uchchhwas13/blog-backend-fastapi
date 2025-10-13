from src.schemas.blog import AddBlogPostPayload, UpdateBlogPostPayload
from src.services.file_service import FileService
from src.exceptions import ValidationError
from fastapi import Depends, UploadFile, Form
from typing import Annotated

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
    if not any([
        cover_image and cover_image.filename,
        title,
        body
    ]):
        raise ValidationError(
            "At least one field (coverImage, title, or body) must be provided.")

    image_path = None
    if cover_image and cover_image.filename:
        image_path = await file_service.save_uploaded_file(file=cover_image)
    return UpdateBlogPostPayload(
        title=title,
        body=body,
        cover_image_url=image_path
    )

UpdateBlogDataDep = Annotated[UpdateBlogPostPayload, Depends(update_blog_data)]
