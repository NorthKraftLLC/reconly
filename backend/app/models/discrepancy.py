"""Discrepancy model."""

import uuid
from enum import Enum as PyEnum

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class DiscrepancyType(PyEnum):
    QUANTITY_MISMATCH = "quantity_mismatch"
    COST_MISMATCH = "cost_mismatch"
    MISSING_ITEM = "missing_item"
    EXTRA_ITEM = "extra_item"
    STALE_DATA = "stale_data"


class Severity(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Discrepancy(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "discrepancies"

    reconciliation_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("reconciliations.id", ondelete="CASCADE"))
    company_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("companies.id", ondelete="CASCADE"))
    inventory_item_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("inventory_items.id", ondelete="SET NULL"), nullable=True
    )
    item_name: Mapped[str] = mapped_column(String(500), nullable=False)
    item_sku: Mapped[str | None] = mapped_column(String(100), nullable=True)
    system_quantity: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    source_quantity: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    quantity_difference: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    system_cost: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    source_cost: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    cost_difference: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)
    discrepancy_type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(Uuid(), ForeignKey("users.id"), nullable=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
