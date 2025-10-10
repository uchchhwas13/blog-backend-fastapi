import time
from fastapi import UploadFile, Form, APIRouter, HTTPException, status
from pathlib import Path
from src.exceptions import InvalidCredentialsError
from src.schemas.api_response import APIResponse
from src.schemas.user import LogOutResponse, LoginResponse, LogoutRequestModel, TokenPairResponse, TokenRefreshRequest, UserCreateModel, UserLoginModel, UserModel, UserResponse
from src.services.auth_service import AuthService
from typing import Annotated
from fastapi import Depends
from src.utils import create_access_token, create_refresh_token, validate_file, verify_password, verify_refresh_token
from src.dependencies_repositories import UserRepositoryDep

auth_router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def user_data_with_image(
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_image: UploadFile | None = Form(
        None, alias="profileImage"),
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
        image_path = "/uploads/default.jpg"

    return UserCreateModel(
        name=fullname,
        email=email,
        password=password,
        profile_image_url=image_path,
    )


@auth_router.post("/signup", response_model=APIResponse[UserModel], status_code=status.HTTP_201_CREATED)
async def create_user(
    user_repo: UserRepositoryDep,
    user_data: UserCreateModel = Depends(user_data_with_image),
):
    auth_service = AuthService(user_repo)

    if await auth_service.user_exists(user_data.email):
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    new_user = await auth_service.create_user(user_data)
    return APIResponse(data=new_user, message="User created successfully", success=True)


@auth_router.post('/signin', response_model=APIResponse[LoginResponse], status_code=status.HTTP_200_OK)
async def login_user(login_data: UserLoginModel, user_repo: UserRepositoryDep):
    auth_service = AuthService(user_repo)
    email = login_data.email
    password = login_data.password

    user = await auth_service.get_user_by_email(email)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            access_token = create_access_token(user_data={
                'email': user.email,
                'user_id': str(user.id),
                'role': user.role
            })

            refresh_token = create_refresh_token(
                user_data={
                    'email': user.email,
                    'user_id': str(user.id),
                    'role': user.role
                }
            )

            await auth_service.save_refresh_token(user, refresh_token)

            return APIResponse(data=LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=UserResponse(
                    email=user.email,
                    id=str(user.id),
                    name=user.name
                )
            ), message="Login successful", success=True)

    raise InvalidCredentialsError()


@auth_router.post('/token/refresh', response_model=APIResponse[TokenPairResponse], status_code=status.HTTP_201_CREATED)
async def refresh_access_token(request_body: TokenRefreshRequest, user_repo: UserRepositoryDep):
    auth_service = AuthService(user_repo)
    token_payload = verify_refresh_token(request_body.refresh_token)
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired refresh token"
        )

    user_id = token_payload.get("user", {}).get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload"
        )

    tokenResponse = await auth_service.refresh_tokens(
        request_body.refresh_token, user_id
    )
    return APIResponse(data=tokenResponse, message="Token refreshed successfully", success=True)


@auth_router.post('/logout', response_model=LogOutResponse, status_code=status.HTTP_200_OK)
async def log_out_user(request_model: LogoutRequestModel, user_repo: UserRepositoryDep):
    auth_service = AuthService(user_repo)
    await auth_service.remove_refresh_token(request_model.user_id)

    return LogOutResponse(message="Logged out successfully", success=True)
