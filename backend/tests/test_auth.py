from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_signup_success(
        self,
        async_client: AsyncClient,
        mock_supabase_client: MagicMock,
        mock_user_response: dict[str, Any],
        mock_session_response: dict[str, Any],
    ) -> None:
        """Test successful user signup."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.model_dump.return_value = mock_user_response
        mock_response.session = MagicMock()
        mock_response.session.model_dump.return_value = mock_session_response

        mock_supabase_client.auth.sign_up.return_value = mock_response

        with patch(
            "app.services.auth.get_supabase_client", return_value=mock_supabase_client
        ):
            response = await async_client.post(
                "/api/v1/auth/signup",
                json={"email": "test@example.com", "password": "TestPassword123!"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user"]["email"] == "test@example.com"
        assert data["session"]["access_token"] == "test-access-token"

    @pytest.mark.asyncio
    async def test_signup_invalid_email(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test signup with invalid email."""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={"email": "invalid-email", "password": "TestPassword123!"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_signin_success(
        self,
        async_client: AsyncClient,
        mock_supabase_client: MagicMock,
        mock_user_response: dict[str, Any],
        mock_session_response: dict[str, Any],
    ) -> None:
        """Test successful user signin."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.model_dump.return_value = mock_user_response
        mock_response.session = MagicMock()
        mock_response.session.model_dump.return_value = mock_session_response

        mock_supabase_client.auth.sign_in_with_password.return_value = mock_response

        with patch(
            "app.services.auth.get_supabase_client", return_value=mock_supabase_client
        ):
            response = await async_client.post(
                "/api/v1/auth/signin",
                json={"email": "test@example.com", "password": "TestPassword123!"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user"]["email"] == "test@example.com"
        assert data["session"]["access_token"] == "test-access-token"

    @pytest.mark.asyncio
    async def test_signin_invalid_credentials(
        self,
        async_client: AsyncClient,
        mock_supabase_client: MagicMock,
    ) -> None:
        """Test signin with invalid credentials."""
        mock_supabase_client.auth.sign_in_with_password.side_effect = Exception(
            "Invalid credentials"
        )

        with patch(
            "app.services.auth.get_supabase_client", return_value=mock_supabase_client
        ):
            response = await async_client.post(
                "/api/v1/auth/signin",
                json={"email": "test@example.com", "password": "WrongPassword"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_me_success(
        self,
        async_client: AsyncClient,
        mock_supabase_client: MagicMock,
        mock_user_response: dict[str, Any],
    ) -> None:
        """Test getting current user information."""
        # Mock the Supabase get_user response
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.model_dump.return_value = mock_user_response

        mock_supabase_client.auth.get_user.return_value = mock_response

        with patch(
            "app.services.auth.get_supabase_client", return_value=mock_supabase_client
        ):
            response = await async_client.get(
                "/api/v1/auth/me",
                headers={"Authorization": "Bearer test-access-token"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["id"] == "test-user-id"

    @pytest.mark.asyncio
    async def test_get_me_unauthorized(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test getting current user without authentication."""
        response = await async_client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self,
        async_client: AsyncClient,
        mock_supabase_client: MagicMock,
        mock_user_response: dict[str, Any],
        mock_session_response: dict[str, Any],
    ) -> None:
        """Test refreshing access token."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.user = MagicMock()
        mock_response.user.model_dump.return_value = mock_user_response
        mock_response.session = MagicMock()
        mock_response.session.model_dump.return_value = mock_session_response

        mock_supabase_client.auth.refresh_session.return_value = mock_response

        with patch(
            "app.services.auth.get_supabase_client", return_value=mock_supabase_client
        ):
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "test-refresh-token"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session"]["access_token"] == "test-access-token"
