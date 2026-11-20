"""Sync history log for tracking data source synchronization."""

from sqlalchemy import JSON, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

import enum
from datetime import UTC, datetime
from app.models.base import Base, UUIDMixin


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"  # Some items synced, some failed


class SyncLog(UUIDMixin, Base):
    __tablename__ = "sync_logs"

    connection_id: Mapped[str] = mapped_column(String, ForeignKey("connections.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[SyncStatus] = mapped_column(SAEnum(SyncStatus), default=SyncStatus.PENDING)
    items_fetched: Mapped[int] = mapped_column(Integer, default=0)
    items_imported: Mapped[int] = mapped_column(Integer, default=0)
    items_updated: Mapped[int] = mapped_column(Integer, default=0)
    items_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_data_preview: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # First 5 items for debugging
    started_at: Mapped[str] = mapped_column(String, default=lambda: datetime.now(UTC).isoformat())
    completed_at: Mapped[str | None] = mapped_column(String, nullable=True)
