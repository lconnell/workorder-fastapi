from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.auth import AuthService


class TestAuthService:
    """Test AuthService class methods."""

    @pytest.fixture
    def auth_service(self, mock_supabase_client: MagicMock) -> AuthService:
        """Create AuthService instance with mocked client."""
        with patch(
            "app.services.auth.get_supabase_client", return_value=mock_supabase_client
        ):
            return AuthService()

    @pytest.mark.asyncio
    async def test_sign_up_success(
        self,
        auth_service: AuthService,
        mock_user_response: dict[str, Any],
        mock_session_response: dict[str, Any],
    ) -> None:
        """Test successful sign up."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.model_dump.return_value = mock_user_response
        mock_response.session = MagicMock()
        mock_response.session.model_dump.return_value = mock_session_response

        auth_service.supabase.auth.sign_up.return_value = mock_response

        result = await auth_service.sign_up("test@example.com", "password123")

        assert result["user"]["email"] == "test@example.com"
        assert result["session"]["access_token"] == "test-access-token"

    @pytest.mark.asyncio
    async def test_sign_up_failure(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test sign up failure."""
        auth_service.supabase.auth.sign_up.side_effect = Exception(
            "User already exists"
        )

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.sign_up("test@example.com", "password123")

        assert exc_info.value.status_code == 400
        assert "User already exists" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_sign_in_success(
        self,
        auth_service: AuthService,
        mock_user_response: dict[str, Any],
        mock_session_response: dict[str, Any],
    ) -> None:
        """Test successful sign in."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.model_dump.return_value = mock_user_response
        mock_response.session = MagicMock()
        mock_response.session.model_dump.return_value = mock_session_response

        auth_service.supabase.auth.sign_in_with_password.return_value = mock_response

        result = await auth_service.sign_in("test@example.com", "password123")

        assert result["user"]["email"] == "test@example.com"
        assert result["session"]["access_token"] == "test-access-token"

    @pytest.mark.asyncio
    async def test_sign_in_invalid_credentials(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test sign in with invalid credentials."""
        auth_service.supabase.auth.sign_in_with_password.side_effect = Exception(
            "Invalid login credentials"
        )

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.sign_in("test@example.com", "wrongpassword")

        assert exc_info.value.status_code == 401
        assert "Invalid login credentials" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_success(
        self,
        auth_service: AuthService,
        mock_user_response: dict[str, Any],
    ) -> None:
        """Test getting current user."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.model_dump.return_value = mock_user_response

        auth_service.supabase.auth.get_user.return_value = mock_response

        result = await auth_service.get_current_user("test-access-token")

        assert result["email"] == "test@example.com"
        assert result["id"] == "test-user-id"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test getting current user with invalid token."""
        auth_service.supabase.auth.get_user.side_effect = Exception("Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.get_current_user("invalid-token")

        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self,
        auth_service: AuthService,
        mock_user_response: dict[str, Any],
        mock_session_response: dict[str, Any],
    ) -> None:
        """Test refreshing token."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.model_dump.return_value = mock_user_response
        mock_response.session = MagicMock()
        mock_response.session.model_dump.return_value = mock_session_response

        auth_service.supabase.auth.refresh_session.return_value = mock_response

        result = await auth_service.refresh_token("test-refresh-token")

        assert result["session"]["access_token"] == "test-access-token"

    @pytest.mark.asyncio
    async def test_sign_out_success(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test signing out."""
        auth_service.supabase.auth.set_session = MagicMock()
        auth_service.supabase.auth.sign_out = MagicMock()

        result = await auth_service.sign_out("test-access-token")

        assert result["message"] == "Successfully signed out"
        auth_service.supabase.auth.set_session.assert_called_once_with(
            "test-access-token", ""
        )
        auth_service.supabase.auth.sign_out.assert_called_once()
