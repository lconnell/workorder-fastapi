from pydantic import BaseModel, EmailStr


class UserSignUp(BaseModel):
    email: EmailStr
    password: str


class UserSignIn(BaseModel):
    email: EmailStr
    password: str


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str
    updated_at: str | None = None
    email_confirmed_at: str | None = None
    phone: str | None = None
    last_sign_in_at: str | None = None


class SessionResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    expires_at: int


class AuthResponse(BaseModel):
    user: UserResponse
    session: SessionResponse | None = None


class MessageResponse(BaseModel):
    message: str
