"""Auth service for user creation, authentication, and token generation."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import CreateUser, TokenResponse


async def create_user(db: AsyncSession, data: CreateUser) -> User:
    existing = await db.execute(select(User).where(User.email == data.email.lower()))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")
    user = User(
        email=data.email.lower(),
        hashed_password=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


async def create_tokens(user: User) -> TokenResponse:
    access = create_access_token(user.id)
    refresh = create_access_token(user.id)
    return TokenResponse(access_token=access, refresh_token=refresh)
