"""
VoiceFlow AI — Auth Schemas
Pydantic request/response models for authentication endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Request Schemas ──

class TenantSetupRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    website: Optional[str] = None
    services: Optional[list[str]] = None


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)
    company_name: str = Field(..., min_length=2, max_length=255)
    company_slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Response Schemas ──

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    tenant_id: UUID

    model_config = {"from_attributes": True}


class TenantResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    subscription_plan: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    user: UserResponse
    tenant: TenantResponse
    tokens: TokenResponse
