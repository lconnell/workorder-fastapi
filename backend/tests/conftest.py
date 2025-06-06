import os
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_supabase_client() -> MagicMock:
    """Mock Supabase client for testing."""
    mock_client = MagicMock()

    # Mock auth methods
    mock_auth = MagicMock()
    mock_client.auth = mock_auth

    return mock_client


@pytest.fixture
def mock_user_response() -> dict[str, Any]:
    """Mock user response data."""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "email_confirmed_at": "2024-01-01T00:00:00Z",
        "phone": None,
        "last_sign_in_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_session_response() -> dict[str, Any]:
    """Mock session response data."""
    return {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "token_type": "bearer",
        "expires_in": 3600,
        "expires_at": 1704067200,
    }


@pytest.fixture(autouse=True)
def set_test_env_vars() -> None:
    """Set test environment variables."""
    os.environ["SUPABASE_URL"] = "https://test.supabase.co"
    os.environ["SUPABASE_KEY"] = "test-anon-key"
    os.environ["SUPABASE_SERVICE_KEY"] = "test-service-key"
    os.environ["SECRET_KEY"] = "test-secret-key"
