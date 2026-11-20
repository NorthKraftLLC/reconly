"""Connector framework for data source integrations (suppliers, POS, stores, marketplaces)."""

import csv
import io
import json
import logging
import re
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.connection import Connection, ConnectionRole, ConnectionType
from app.models.inventory_item import InventoryItem
from app.models.sync_log import SyncLog, SyncStatus

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Base class for all data source connectors."""

    @abstractmethod
    async def fetch_inventory(self, connection: Connection) -> list[dict]:
        """Fetch raw inventory data from the source. Returns list of dicts with at least: sku, name, quantity, price."""
        ...

    @abstractmethod
    async def test_connection(self, credentials: dict, config: dict) -> dict:
        """Test if credentials are valid. Returns {'ok': bool, 'message': str, 'detail': dict}."""
        ...

    async def normalize_items(self, raw_items: list[dict]) -> list[dict]:
        """Normalize raw items into standard format."""
        normalized = []
        for item in raw_items:
            normalized.append({
                "sku": str(item.get("sku", item.get("product_id", item.get("item_code", ""))).strip()),
                "name": str(item.get("name", item.get("title", item.get("product_name", "Unknown"))).strip()),
                "quantity": self._parse_quantity(item.get("quantity", item.get("qty", item.get("stock", 0)))),
                "price": self._parse_price(item.get("price", item.get("unit_price", item.get("cost", 0)))),
                "category": str(item.get("category", item.get("type", ""))).strip() or None,
                "source_data": item,  # Keep raw data for reference
            })
        # Filter out items without SKU
        return [i for i in normalized if i["sku"]]

    @staticmethod
    def _parse_quantity(val: Any) -> int:
        try:
            return int(float(str(val).replace(",", "").replace("$", "")))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _parse_price(val: Any) -> float:
        try:
            return float(str(val).replace(",", "").replace("$", ""))
        except (ValueError, TypeError):
            return 0.0


class CSVConnector(BaseConnector):
    """Handle CSV/Excel file imports from suppliers."""
    connection_type = ConnectionType.CSV_IMPORT

    async def fetch_inventory(self, connection: Connection) -> list[dict]:
        # CSV data is stored in config['csv_data'] after upload
        raw = connection.config.get("csv_data", [])
        if isinstance(raw, str):
            raw = json.loads(raw)
        return raw if isinstance(raw, list) else []

    async def test_connection(self, credentials: dict, config: dict) -> dict:
        raw = config.get("csv_data", [])
        count = len(raw) if isinstance(raw, list) else 0
        return {"ok": count > 0, "message": f"CSV has {count} items", "detail": {"items": count}}

    @staticmethod
    def parse_csv_text(csv_text: str) -> list[dict]:
        """Parse CSV text into list of dicts."""
        reader = csv.DictReader(io.StringIO(csv_text))
        return [dict(row) for row in reader]

    @staticmethod
    def parse_csv_bytes(csv_bytes: bytes) -> list[dict]:
        """Parse CSV bytes into list of dicts."""
        text = csv_bytes.decode("utf-8-sig")  # Handle BOM
        return CSVConnector.parse_csv_text(text)


class ShopifyConnector(BaseConnector):
    """Connect to Shopify stores via Admin API."""
    connection_type = ConnectionType.SHOPIFY

    async def fetch_inventory(self, connection: Connection) -> list[dict]:
        shop = connection.credentials.get("shop", "")
        token = connection.credentials.get("access_token", "")
        if not shop or not token:
            raise ValueError("Shopify shop URL and access_token required")

        async with httpx.AsyncClient(timeout=60) as client:
            headers = {"X-Shopify-Access-Token": token}
            items = []
            page = 1
            while True:
                resp = await client.get(
                    f"https://{shop}/admin/api/2024-01/inventory_levels.json",
                    headers=headers,
                    params={"limit": 250, "page": page},
                )
                if resp.status_code != 200:
                    raise ValueError(f"Shopify API error: {resp.status_code} {resp.text[:200]}")
                data = resp.json()
                levels = data.get("inventory_levels", [])
                for level in levels:
                    item_id = level.get("inventory_item_id")
                    location_avail = 0
                    for loc in level.get("available", []):
                        location_avail += loc.get("available", 0)
                    items.append({
                        "sku": level.get("sku", f"shopify-{item_id}"),
                        "name": level.get("product_title", f"Item {item_id}"),
                        "quantity": location_avail,
                        "price": level.get("price", 0),
                    })
                if len(levels) < 250:
                    break
                page += 1
        return items

    async def test_connection(self, credentials: dict, config: dict) -> dict:
        shop = credentials.get("shop", "")
        token = credentials.get("access_token", "")
        if not shop or not token:
            return {"ok": False, "message": "Shop and access_token required"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"https://{shop}/admin/api/2024-01/shop.json",
                    headers={"X-Shopify-Access-Token": token},
                )
                if resp.status_code == 200:
                    shop_data = resp.json().get("shop", {})
                    return {"ok": True, "message": f"Connected to {shop_data.get('name', shop)}", "detail": shop_data}
                return {"ok": False, "message": f"API error: {resp.status_code}"}
        except Exception as e:
            return {"ok": False, "message": str(e)}


class SquareConnector(BaseConnector):
    """Connect to Square Point of Sale."""
    connection_type = ConnectionType.SQUARE

    async def fetch_inventory(self, connection: Connection) -> list[dict]:
        access_token = connection.credentials.get("access_token", "")
        location_id = connection.credentials.get("location_id", "")
        if not access_token:
            raise ValueError("Square access_token required")

        async with httpx.AsyncClient(timeout=60) as client:
            headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
            items = []
            cursor = None
            while True:
                params = {"limit": 100}
                if cursor:
                    params["cursor"] = cursor
                resp = await client.post(
                    "https://connect.squareup.com/v2/catalog/list",
                    headers=headers,
                    json={"types": ["ITEM"]},
                    params=params,
                )
                if resp.status_code != 200:
                    raise ValueError(f"Square API error: {resp.status_code} {resp.text[:200]}")
                data = resp.json()
                for obj in data.get("objects", []):
                    item_data = obj.get("item_data", {})
                    items.append({
                        "sku": item_data.get("sku", obj.get("id", "")),
                        "name": item_data.get("name", "Unknown"),
                        "quantity": 0,  # Square tracks via inventory API
                        "price": item_data.get("variant_data", {}).get("price_money", {}).get("amount", 0) / 100,
                    })
                cursor = data.get("cursor")
                if not cursor:
                    break
        return items

    async def test_connection(self, credentials: dict, config: dict) -> dict:
        token = credentials.get("access_token", "")
        if not token:
            return {"ok": False, "message": "access_token required"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    "https://connect.squareup.com/v2/locations",
                    headers={"Authorization": f"Bearer {token}"},
                )
                if resp.status_code == 200:
                    locations = resp.json().get("locations", [])
                    return {"ok": True, "message": f"Connected ({len(locations)} locations)", "detail": {"locations": locations}}
                return {"ok": False, "message": f"API error: {resp.status_code}"}
        except Exception as e:
            return {"ok": False, "message": str(e)}


class QuickBooksConnector(BaseConnector):
    """Connect to QuickBooks Online via Intuit API."""
    connection_type = ConnectionType.QUICKBOOKS

    async def fetch_inventory(self, connection: Connection) -> list[dict]:
        access_token = connection.credentials.get("access_token", "")
        realm_id = connection.credentials.get("realm_id", "")  # Company ID
        if not access_token or not realm_id:
            raise ValueError("QuickBooks access_token and realm_id required")

        async with httpx.AsyncClient(timeout=60) as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            resp = await client.get(
                f"https://quickbooks.api.intuit.com/v3/company/{realm_id}/query",
                headers=headers,
                params={"query": "SELECT * FROM Inventory"},
            )
            if resp.status_code != 200:
                raise ValueError(f"QuickBooks API error: {resp.status_code} {resp.text[:200]}")
            data = resp.json()
            items = []
            for qbo_item in data.get("QueryResponse", {}).get("Inventory", []):
                items.append({
                    "sku": qbo_item.get("SKU", ""),
                    "name": qbo_item.get("Name", "Unknown"),
                    "quantity": self._parse_quantity(qbo_item.get("QtyOnHand", 0)),
                    "price": self._parse_price(qbo_item.get("UnitCost", 0)),
                })
            return items

    async def test_connection(self, credentials: dict, config: dict) -> dict:
        token = credentials.get("access_token", "")
        realm = credentials.get("realm_id", "")
        if not token or not realm:
            return {"ok": False, "message": "access_token and realm_id required"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"https://quickbooks.api.intuit.com/v3/company/{realm}/companyinfo",
                    headers={"Authorization": f"Bearer {token}"},
                )
                if resp.status_code == 200:
                    info = resp.json().get("CompanyInfo", {})
                    return {"ok": True, "message": f"Connected to {info.get('CompanyName', realm)}", "detail": info}
                return {"ok": False, "message": f"API error: {resp.status_code}"}
        except Exception as e:
            return {"ok": False, "message": str(e)}


class WooCommerceConnector(BaseConnector):
    """Connect to WooCommerce stores."""
    connection_type = ConnectionType.WOOCOMMERCE

    async def fetch_inventory(self, connection: Connection) -> list[dict]:
        store_url = connection.credentials.get("store_url", "").rstrip("/")
        consumer_key = connection.credentials.get("consumer_key", "")
        consumer_secret = connection.credentials.get("consumer_secret", "")
        if not store_url or not consumer_key or not consumer_secret:
            raise ValueError("WooCommerce store_url, consumer_key, and consumer_secret required")

        async with httpx.AsyncClient(timeout=60) as client:
            items = []
            page = 1
            while True:
                resp = await client.get(
                    f"{store_url}/wp-json/wc/v3/products",
                    auth=(consumer_key, consumer_secret),
                    params={"per_page": 100, "page": page, "type": "simple,variable"},
                )
                if resp.status_code != 200:
                    raise ValueError(f"WooCommerce API error: {resp.status_code} {resp.text[:200]}")
                products = resp.json()
                for p in products:
                    items.append({
                        "sku": p.get("sku", f"woo-{p.get('id')}"),
                        "name": p.get("name", "Unknown"),
                        "quantity": self._parse_quantity(p.get("stock_quantity", 0)),
                        "price": self._parse_price(p.get("regular_price", 0)),
                        "category": p.get("categories", [{}])[0].get("name") if p.get("categories") else None,
                    })
                if len(products) < 100:
                    break
                page += 1
            return items

    async def test_connection(self, credentials: dict, config: dict) -> dict:
        url = credentials.get("store_url", "").rstrip("/")
        key = credentials.get("consumer_key", "")
        secret = credentials.get("consumer_secret", "")
        if not url or not key or not secret:
            return {"ok": False, "message": "store_url, consumer_key, and consumer_secret required"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{url}/wp-json/wc/v3/products",
                    auth=(key, secret),
                    params={"per_page": 1},
                )
                if resp.status_code == 200:
                    return {"ok": True, "message": f"Connected to {url}", "detail": {"products_found": True}}
                return {"ok": False, "message": f"API error: {resp.status_code}"}
        except Exception as e:
            return {"ok": False, "message": str(e)}


class CustomAPIConnector(BaseConnector):
    """Generic REST API connector for custom integrations."""
    connection_type = ConnectionType.CUSTOM_API

    async def fetch_inventory(self, connection: Connection) -> list[dict]:
        url = connection.credentials.get("api_url", "")
        headers = connection.credentials.get("headers", {})
        auth_token = connection.credentials.get("auth_token", "")
        if not url:
            raise ValueError("API URL required")

        if auth_token and not headers.get("Authorization"):
            headers["Authorization"] = f"Bearer {auth_token}"

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise ValueError(f"API error: {resp.status_code} {resp.text[:200]}")
            data = resp.json()
            # Try common response patterns
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                for key in ("items", "data", "products", "inventory", "results"):
                    if key in data and isinstance(data[key], list):
                        return data[key]
            return [data] if isinstance(data, dict) else []

    async def test_connection(self, credentials: dict, config: dict) -> dict:
        url = credentials.get("api_url", "")
        if not url:
            return {"ok": False, "message": "api_url required"}
        try:
            headers = credentials.get("headers", {})
            token = credentials.get("auth_token", "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    return {"ok": True, "message": f"Connected to {url}", "detail": {"status": resp.status_code}}
                return {"ok": False, "message": f"API error: {resp.status_code}"}
        except Exception as e:
            return {"ok": False, "message": str(e)}


class GoogleSheetsConnector(BaseConnector):
    """Connect to Google Sheets for supplier/store inventory feeds."""
    connection_type = ConnectionType.GOOGLE_SHEETS

    async def fetch_inventory(self, connection: Connection) -> list[dict]:
        sheet_id = connection.credentials.get("sheet_id", "")
        range_name = connection.credentials.get("range", "Sheet1!A1:Z")
        service_account_json = connection.credentials.get("service_account_json")
        if not sheet_id or not service_account_json:
            raise ValueError("Google Sheets sheet_id and service_account_json required")

        # Use Google Sheets API
        # Note: In production, use google-auth library
        # For now, use the public CSV export as fallback
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                # Public sheet export (works for shared sheets)
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
                resp = await client.get(csv_url)
                if resp.status_code == 200:
                    return CSVConnector.parse_csv_text(resp.text)
                raise ValueError("Sheet not publicly accessible - configure service account")
        except Exception as e:
            raise ValueError(f"Google Sheets error: {str(e)}")

    async def test_connection(self, credentials: dict, config: dict) -> dict:
        sheet_id = credentials.get("sheet_id", "")
        if not sheet_id:
            return {"ok": False, "message": "sheet_id required"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0")
                if resp.status_code == 200:
                    items = CSVConnector.parse_csv_text(resp.text)
                    return {"ok": True, "message": f"Sheet accessible ({len(items)} rows)", "detail": {"rows": len(items)}}
                return {"ok": False, "message": "Sheet not accessible"}
        except Exception as e:
            return {"ok": False, "message": str(e)}


# Connector registry
CONNECTOR_MAP: dict[ConnectionType, type[BaseConnector]] = {
    ConnectionType.CSV_IMPORT: CSVConnector,
    ConnectionType.SHOPIFY: ShopifyConnector,
    ConnectionType.SQUARE: SquareConnector,
    ConnectionType.QUICKBOOKS: QuickBooksConnector,
    ConnectionType.WOOCOMMERCE: WooCommerceConnector,
    ConnectionType.CUSTOM_API: CustomAPIConnector,
    ConnectionType.GOOGLE_SHEETS: GoogleSheetsConnector,
}


def get_connector(connection_type: ConnectionType) -> BaseConnector:
    """Get connector instance for a connection type."""
    cls = CONNECTOR_MAP.get(connection_type)
    if not cls:
        raise ValueError(f"No connector for type: {connection_type}")
    return cls()


async def sync_connection(db: AsyncSession, connection: Connection) -> SyncLog:
    """Execute a full sync: fetch data from source, normalize, upsert inventory items."""
    sync_log = SyncLog(
        connection_id=connection.id,
        company_id=connection.company_id,
        status=SyncStatus.IN_PROGRESS,
    )
    db.add(sync_log)
    await db.flush()

    try:
        connector = get_connector(connection.connection_type)
        logger.info(f"Fetching inventory from connection {connection.id}, type={connection.connection_type}")
        raw_items = await connector.fetch_inventory(connection)
        logger.info(f"Fetched {len(raw_items)} raw items")
        normalized = connector.normalize_items(raw_items)
        logger.info(f"Normalized {len(normalized)} items")

        sync_log.items_fetched = len(raw_items)
        sync_log.raw_data_preview = raw_items[:5] if raw_items else None

        # Upsert inventory items
        imported = 0
        updated = 0
        failed = 0

        logger.info(f"Starting upsert loop, company_id={connection.company_id}")
        for item in normalized:
            try:
                # Check if item exists by SKU + company
                existing = await db.execute(
                    select(InventoryItem).where(
                        InventoryItem.sku == item["sku"],
                        InventoryItem.company_id == connection.company_id,
                    )
                )
                existing_item = existing.scalar_one_or_none()

                if existing_item:
                    existing_item.quantity_on_hand = item["quantity"]
                    existing_item.unit_cost = item["price"]
                    existing_item.name = item["name"]
                    existing_item.category = item.get("category")
                    existing_item.source_connection_id = str(connection.id)
                    updated += 1
                else:
                    new_item = InventoryItem(
                        company_id=connection.company_id,
                        name=item["name"],
                        sku=item["sku"],
                        quantity_on_hand=item["quantity"],
                        unit_cost=item["price"],
                        category=item.get("category"),
                        source_connection_id=str(connection.id),
                    )
                    db.add(new_item)
                    imported += 1
            except Exception as e:
                logger.error(f"Failed to import item {item.get('sku')}: {e}")
                failed += 1

        sync_log.items_imported = imported
        sync_log.items_updated = updated
        sync_log.items_failed = failed
        sync_log.status = SyncStatus.SUCCESS if failed == 0 else (SyncStatus.PARTIAL if imported + updated > 0 else SyncStatus.FAILED)
        sync_log.completed_at = datetime.now(UTC).isoformat()

        # Update connection metadata
        connection.last_sync_at = datetime.now(UTC).isoformat()
        connection.last_sync_status = sync_log.status.value
        connection.items_count = imported + updated

        return sync_log

    except Exception as e:
        logger.error(f"Sync failed for connection {connection.id}: {e}")
        sync_log.status = SyncStatus.FAILED
        sync_log.error_message = str(e)[:2000]
        sync_log.completed_at = datetime.now(UTC).isoformat()
        connection.last_sync_status = "failed"
        return sync_log  # Return so get_async_session auto-commits the failure
