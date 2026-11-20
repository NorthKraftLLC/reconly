"""Data source connection model (suppliers, POS, stores, warehouses)."""

from sqlalchemy import JSON, Boolean, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

import enum
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
    SUPPLIER = "supplier"          # External supplier inventory feeds
    POS = "pos"                    # Point of sale system
    STORE = "store"                # Physical/online store inventory
    WAREHOUSE = "warehouse"        # Warehouse management system
    ERP = "erp"                    # Enterprise resource planning
    MARKETPLACE = "marketplace"    # Amazon, Walmart, eBay
    CUSTOM = "custom"              # Custom data source


class Connection(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "connections"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    connection_type: Mapped[ConnectionType] = mapped_column(SAEnum(ConnectionType), nullable=False)
    role: Mapped[ConnectionRole] = mapped_column(SAEnum(ConnectionRole), nullable=False, default=ConnectionRole.CUSTOM)
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    credentials: Mapped[dict] = mapped_column(JSON, default=dict)  # Encrypted API keys, tokens, URLs
    config: Mapped[dict] = mapped_column(JSON, default=dict)  # Sync interval, mappings, filters
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_sync_status: Mapped[str | None] = mapped_column(String(50), nullable=True)  # success, failed, in_progress
    items_count: Mapped[int | None] = mapped_column(nullable=True)  # Last sync item count
