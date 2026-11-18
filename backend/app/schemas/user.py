from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=12)
    first_name: str | None = None
    last_name: str | None = None
    role: str = "viewer"


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    first_name: str | None = None
    last_name: str | None = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
