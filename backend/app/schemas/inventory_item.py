from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateInventoryItem(BaseModel):
    company_id: UUID
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=2000)
    quantity_on_hand: int = Field(ge=0, default=0)
    unit_cost: float = Field(ge=0, default=0.0)
    currency: str = "USD"
    location: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    reorder_level: int = Field(ge=0, default=0)
    notes: str | None = Field(default=None, max_length=1000)


class UpdateInventoryItem(BaseModel):
    name: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=2000)
    quantity_on_hand: int | None = Field(default=None, ge=0)
    unit_cost: float | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    reorder_level: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=1000)


class BulkUploadItem(BaseModel):
    sku: str
    name: str
    quantity_on_hand: int = Field(ge=0)
    unit_cost: float = Field(ge=0)


class InventoryResponse(BaseModel):
    id: UUID
    company_id: UUID
    sku: str
    name: str
    description: str | None = None
    quantity_on_hand: int
    unit_cost: float
    currency: str
    location: str | None = None
    category: str | None = None
    reorder_level: int
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
