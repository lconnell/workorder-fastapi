from typing import Any

from fastapi import APIRouter, Depends

from app.models.auth import (
    AuthResponse,
    MessageResponse,
    TokenRefresh,
    UserSignIn,
    UserSignUp,
)
from app.services.auth import AuthService, get_current_user_from_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def sign_up(user_data: UserSignUp) -> Any:
    """Register a new user."""
    auth_service = AuthService()
    return await auth_service.sign_up(user_data.email, user_data.password)


@router.post("/signin", response_model=AuthResponse)
async def sign_in(user_data: UserSignIn) -> Any:
    """Sign in an existing user."""
    auth_service = AuthService()
    return await auth_service.sign_in(user_data.email, user_data.password)


@router.post("/signout", response_model=MessageResponse)
async def sign_out(
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> MessageResponse:
    """Sign out the current user."""
    # Note: Supabase handles token invalidation on their end
    # For a production app, you might want to:
    # 1. Add the token to a blacklist
    # 2. Clear any server-side sessions
    # 3. Log the signout event
    return MessageResponse(message="Successfully signed out")


@router.get("/me", response_model=dict[str, Any])
async def get_me(
    current_user: dict[str, Any] = Depends(get_current_user_from_token),
) -> Any:
    """Get current user information."""
    return current_user


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(token_data: TokenRefresh) -> Any:
    """Refresh access token."""
    auth_service = AuthService()
    return await auth_service.refresh_token(token_data.refresh_token)
