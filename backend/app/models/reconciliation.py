"""Reconciliation model."""

import uuid
from enum import Enum as PyEnum

from sqlalchemy import JSON, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class ReconciliationStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Reconciliation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reconciliations"

    company_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("companies.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=ReconciliationStatus.PENDING.value)
    source_file_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    total_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    matched_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    discrepancies_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("users.id"), nullable=False)
