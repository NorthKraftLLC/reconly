"""Data source connection model (suppliers, POS, stores, warehouses)."""

import enum
import uuid

from sqlalchemy import JSON, Boolean, Enum as SAEnum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class ConnectionType(str, enum.Enum):
    """Types of data source connections."""
    CSV_IMPORT = "csv_import"
    SHOPIFY = "shopify"
    SQUARE = "square"
    QUICKBOOKS = "quickbooks"
    WOOCOMMERCE = "woocommerce"
    AMAZON = "amazon"
    WALMART = "walmart"
    NETSUITE = "netsuite"
    SAP = "sap"
    CUSTOM_API = "custom_api"
    GOOGLE_SHEETS = "google_sheets"
    EMAIL_FEED = "email_feed"


class ConnectionRole(str, enum.Enum):
    """Role of this connection in reconciliation."""
    SUPPLIER = "supplier"
    POS = "pos"
    STORE = "store"
    WAREHOUSE = "warehouse"
    ERP = "erp"
    MARKETPLACE = "marketplace"
    CUSTOM = "custom"


class Connection(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "connections"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    connection_type: Mapped[ConnectionType] = mapped_column(SAEnum(ConnectionType), nullable=False)
    role: Mapped[ConnectionRole] = mapped_column(SAEnum(ConnectionRole), nullable=False, default=ConnectionRole.CUSTOM)
    company_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    credentials: Mapped[dict] = mapped_column(JSON, default=dict)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_sync_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    items_count: Mapped[int | None] = mapped_column(nullable=True)
