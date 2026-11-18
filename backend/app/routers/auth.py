"""Authentication router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.user import CreateUser, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import create_user, authenticate, create_tokens
from app.dependencies import get_current_user
from app.models.user import User
from app.core.audit import log_event

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(data: CreateUser, db: AsyncSession = Depends(get_async_session)):
    try:
        user = await create_user(db, data)
        log_event("anonymous", "register", user.email, "success")
        return user
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_async_session)):
    user = await authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tokens = await create_tokens(user)
    log_event(str(user.id), "login", user.email, "success")
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user
