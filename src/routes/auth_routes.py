import time
from fastapi import UploadFile, File, Form, APIRouter, HTTPException, status
from pathlib import Path
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schemas.user import UserCreateModel, UserModel
from src.services.auth_service import AuthService
from src.db.main import get_session
from typing import Annotated
from fastapi import Depends

auth_router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB

auth_service = AuthService()


def validate_file(file: UploadFile, content: bytes) -> None:
    """Validate file type and size."""
    if not file.filename:
        return
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Max size allowed is 1MB"
        )


async def user_data_with_image(
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_image: UploadFile | None = File(None),
) -> UserCreateModel:
    if profile_image:
        content = await profile_image.read()
        validate_file(profile_image, content)

        timestamp = int(time.time())
        file_name = f"{timestamp}-{profile_image.filename}"
        file_path = UPLOAD_DIR / file_name

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        image_path = f"/uploads/{file_name}"
    else:
        image_path = "/uploads/default.png"

    return UserCreateModel(
        name=fullname,
        email=email,
        password=password,
        profile_image=image_path,
    )


@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_data: UserCreateModel = Depends(user_data_with_image),
):
    auth_service = AuthService()

    if await auth_service.user_exists(user_data.email, session):
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    new_user = await auth_service.create_user(user_data, session)
    return new_user
