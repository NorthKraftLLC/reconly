"""Authentication router."""

import re
from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_event
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import CreateUser, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import authenticate, create_tokens, create_user

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


def sanitize_input(value: str) -> str:
    """Strip potentially dangerous characters."""
    return re.sub(r'[<>"\'();\\]', '', value).strip()


@limiter.limit("5/minute")
@router.post("/register", response_model=UserResponse)
async def register(request: Request, data: CreateUser, db: AsyncSession = Depends(get_async_session)):
    try:
        data.email = sanitize_input(data.email)
        user = await create_user(db, data)
        log_event(str(user.id), "register", user.email, "success", ip_address=get_remote_address(request))
        return user
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@limiter.limit("10/minute")
@router.post("/login", response_model=TokenResponse)
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_async_session)):
    email = sanitize_input(data.email)
    user = await authenticate(db, email, data.password)
    if not user:
        log_event("anonymous", "login_failed", email, "failure", ip_address=get_remote_address(request))
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tokens = await create_tokens(user)
    log_event(str(user.id), "login", user.email, "success", ip_address=get_remote_address(request))
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user