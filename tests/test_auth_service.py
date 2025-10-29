import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.auth_service import AuthService
from src.schemas.user import TokenPairResponse
from src.exceptions import ResourceNotFoundError, DatabaseError, AuthorizationError
from src.models.user import User
from src.schemas.user import UserCreateModel


class TestAuthService:
    """Unit tests for AuthService"""

    @pytest.fixture(scope="function")
    def auth_service(self, mock_user_repository: AsyncMock) -> AuthService:
        return AuthService(user_repo=mock_user_repository)

    @pytest.mark.asyncio
    async def test_get_user_by_email_returns_user_when_email_exists(self, auth_service: AuthService, mock_user_repository: AsyncMock, sample_user: User):
        # Arrange
        mock_user_repository.get_by_email.return_value = sample_user

        # Act
        result = await auth_service.get_user_by_email(sample_user.email)

        # Assert
        assert result == sample_user
        mock_user_repository.get_by_email.assert_called_once_with(
            sample_user.email)
