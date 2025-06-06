from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.supabase import get_supabase_client

security = HTTPBearer()


class AuthService:
    def __init__(self) -> None:
        self.supabase = get_supabase_client()

    async def sign_up(self, email: str, password: str) -> dict[str, Any]:
        """Register a new user."""
        try:
            response = self.supabase.auth.sign_up(
                {"email": email, "password": password}
            )
            if response.user:
                return {
                    "user": response.user.model_dump(),
                    "session": (
                        response.session.model_dump() if response.session else None
                    ),
                }
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e

    async def sign_in(self, email: str, password: str) -> dict[str, Any]:
        """Sign in an existing user."""
        try:
            response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if response.user and response.session:
                return {
                    "user": response.user.model_dump(),
                    "session": response.session.model_dump(),
                }
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            ) from e

    async def sign_out(self, access_token: str) -> dict[str, str]:
        """Sign out the current user."""
        try:
            # Set the session with the token before signing out
            self.supabase.auth.set_session(access_token, "")
            self.supabase.auth.sign_out()
            return {"message": "Successfully signed out"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e

    async def get_current_user(self, access_token: str) -> dict[str, Any]:
        """Get the current user from access token."""
        try:
            # Verify token with Supabase
            response = self.supabase.auth.get_user(access_token)
            if response.user:
                user_data: dict[str, Any] = response.user.model_dump()
                return user_data
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            ) from e

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh access token using refresh token."""
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            if response.user and response.session:
                return {
                    "user": response.user.model_dump(),
                    "session": response.session.model_dump(),
                }
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            ) from e


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """Dependency to get current user from JWT token."""
    auth_service = AuthService()
    return await auth_service.get_current_user(credentials.credentials)
