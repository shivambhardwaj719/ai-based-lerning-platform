"""Auth request/response schemas."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")]
    password: Annotated[str, Field(min_length=8, max_length=128)]
    full_name: Annotated[str, Field(min_length=1, max_length=255)]

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False
    device_id: str | None = None
    device_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user_id: uuid.UUID
    requires_2fa: bool = False


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
    all_devices: bool = False


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: Annotated[str, Field(min_length=6, max_length=6, pattern=r"^\d{6}$")]


class EmailVerifyRequest(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: Annotated[str, Field(min_length=8, max_length=128)]


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: Annotated[str, Field(min_length=8, max_length=128)]


class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: list[str]


class TwoFactorVerifyRequest(BaseModel):
    code: Annotated[str, Field(min_length=6, max_length=8)]


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    device_id: str | None = None


class SessionResponse(BaseModel):
    id: uuid.UUID
    device_name: str | None
    device_type: str | None
    ip_address: str | None
    location: dict | None
    last_used_at: datetime
    created_at: datetime
    is_current: bool = False

    class Config:
        from_attributes = True


class UserSessionsResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int


class RevokeSessionRequest(BaseModel):
    session_id: uuid.UUID
