from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateCompany(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    industry: str | None = Field(default=None, max_length=100)


class UpdateCompany(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    industry: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    industry: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
