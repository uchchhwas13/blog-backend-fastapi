import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime

from src.models.user import User
from src.models.blog import Blog
from src.schemas.user import UserCreateModel


@pytest.fixture
def mock_user_repository():
    """Mock UserRepository for testing"""
    return AsyncMock()


@pytest.fixture
def mock_blog_repository():
    """Mock BlogRepository for testing"""
    return AsyncMock()


@pytest.fixture
def mock_blog_like_repository():
    """Mock BlogLikeRepository for testing"""
    return AsyncMock()


@pytest.fixture
def mock_comment_repository():
    """Mock CommentRepository for testing"""
    return AsyncMock()


@pytest.fixture
def sample_user():
    """Sample user for testing"""
    return User(
        id=uuid4(),
        name="John Doe",
        email="john@example.com",
        password_hash="hashed_password",
        role="user",
        refresh_token="sample_refresh_token",
        profile_image_url="profile.jpg",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def sample_blog():
    """Sample blog for testing"""
    return Blog(
        id=uuid4(),
        title="Test Blog",
        body="This is a test blog post",
        cover_image_url="cover.jpg",
        created_by=uuid4(),
        like_count=0,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def sample_user_create_data():
    """Sample user creation data"""
    return UserCreateModel(
        name="John Doe",
        email="john@example.com",
        password="password123"
    )
