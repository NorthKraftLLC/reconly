from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateReconciliation(BaseModel):
    company_id: UUID
    name: str = Field(min_length=1, max_length=200)
    source_file_name: str | None = Field(default=None, max_length=500)
    source_data: dict | None = None


class ReconciliationResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    status: str
    source_file_name: str | None = None
    total_items: int
    matched_items: int
    discrepancies_found: int
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class DiscrepancyResponse(BaseModel):
    id: UUID
    reconciliation_id: UUID
    item_name: str
    item_sku: str | None
    system_quantity: float
    source_quantity: float
    quantity_difference: float
    discrepancy_type: str
    severity: str
    explanation: str
    resolved: bool
    resolved_at: str | None
    reviewer_notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
