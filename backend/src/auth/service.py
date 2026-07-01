"""
VoiceFlow AI — Auth Service
Business logic for tenant creation, user registration, login, and token refresh.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import (
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)
from src.models.tenant import Tenant
from src.models.user import User, UserRole
from src.auth.schemas import RegisterRequest, LoginRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> dict:
        """Register a new tenant with an admin user."""
        # Check if email already exists
        existing = await self.db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise ValueError("Email already registered")

        # Check if slug already exists
        existing_tenant = await self.db.execute(
            select(Tenant).where(Tenant.slug == data.company_slug)
        )
        if existing_tenant.scalar_one_or_none():
            raise ValueError("Company slug already taken")

        # Create tenant
        tenant = Tenant(
            name=data.company_name,
            slug=data.company_slug,
            subscription_plan="free",
            services=[
                "Website Development",
                "Mobile App Development",
                "SaaS Development",
                "AI Automation",
                "Digital Marketing",
                "SEO",
                "Google Ads",
                "Meta Ads",
                "WhatsApp Automation",
                "CRM Development",
                "UI/UX Design",
                "Cloud Solutions",
                "Custom Software",
                "Consulting",
            ],
            ai_personality={
                "name": "VoiceFlow Assistant",
                "tone": "professional_friendly",
                "language_preference": "auto",
                "greeting_style": "warm",
            },
        )
        self.db.add(tenant)
        await self.db.flush()

        # Create admin user
        user = User(
            tenant_id=tenant.id,
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=UserRole.ADMIN,
            last_login=datetime.now(timezone.utc),
        )
        self.db.add(user)
        await self.db.flush()

        # Generate tokens
        tokens = create_token_pair(user.id, tenant.id, user.role.value)

        return {
            "user": user,
            "tenant": tenant,
            "tokens": tokens,
        }

    async def login(self, data: LoginRequest) -> dict:
        """Authenticate user and return tokens."""
        result = await self.db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await self.db.flush()

        # Get tenant
        tenant_result = await self.db.execute(
            select(Tenant).where(Tenant.id == user.tenant_id)
        )
        tenant = tenant_result.scalar_one()

        # Generate tokens
        tokens = create_token_pair(user.id, tenant.id, user.role.value)

        return {
            "user": user,
            "tenant": tenant,
            "tokens": tokens,
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        """Issue new token pair from a valid refresh token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = UUID(payload["sub"])
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise ValueError("User not found or deactivated")

        tokens = create_token_pair(user.id, user.tenant_id, user.role.value)
        return {"tokens": tokens}

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by their ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_tenant_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get a tenant by ID."""
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        return result.scalar_one_or_none()
