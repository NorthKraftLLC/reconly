"""Integrations/Connections router for managing data sources."""

import json as json_mod
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import log_event
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.connection import Connection, ConnectionType, ConnectionRole
from app.models.sync_log import SyncLog
from app.models.user import User
from app.services.connector_service import (
    sync_connection,
    CSVConnector,
    CONNECTOR_MAP,
    get_connector,
)
from app.services.inventory_service import get_company_owned

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/types")
async def get_connector_types():
    """Return all available connector types with their info."""
    return {
        "types": [
            {"type": ct.value, "name": cls.__name__.replace("Connector", ""), "description": cls.__doc__ or ""}
            for ct, cls in CONNECTOR_MAP.items()
        ]
    }


@router.get("/")
async def list_connections(db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    """List all connections for the current user's companies only."""
    from app.models.company import Company
    user_companies = await db.execute(select(Company.id).where(Company.owner_id == user.id))
    company_ids = [c[0] for c in user_companies.all()]
    if not company_ids:
        return []
    result = await db.execute(
        select(Connection).where(Connection.company_id.in_(company_ids)).order_by(Connection.created_at.desc())
    )
    return result.scalars().all()


@router.post("/")
async def create_connection(
    name: str = Form(...),
    connection_type: str = Form(...),
    role: str = Form("custom"),
    company_id: str = Form(...),
    credentials: str = Form("{}"),
    config: str = Form("{}"),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Create a new data source connection."""
    try:
        conn_type = ConnectionType(connection_type)
        conn_role = ConnectionRole(role)
        creds = json_mod.loads(credentials)
        cfg = json_mod.loads(config)
        company_uuid = UUID(company_id)
    except (ValueError, json_mod.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    company = await get_company_owned(db, company_uuid, user.id)
    if not company:
        raise HTTPException(status_code=403, detail="Company not found or access denied")

    connection = Connection(
        name=name, connection_type=conn_type, role=conn_role,
        company_id=company_uuid, credentials=creds, config=cfg,
    )
    db.add(connection)
    await db.flush()
    await db.refresh(connection)
    log_event(str(user.id), "create_connection", str(connection.id), "success")
    return {"id": str(connection.id), "name": connection.name, "type": connection.connection_type.value, "role": connection.role.value}


@router.post("/{connection_id}/test")
async def test_connection_ep(
    connection_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Test if a connection's credentials are valid."""
    conn = await db.execute(select(Connection).where(Connection.id == UUID(connection_id)))
    connection = conn.scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if not await get_company_owned(db, connection.company_id, user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    connector = get_connector(connection.connection_type)
    result = await connector.test_connection(connection.credentials, connection.config)
    return {"ok": result["ok"], "message": result["message"], "detail": result.get("detail")}


@router.post("/{connection_id}/sync")
async def trigger_sync(
    connection_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Trigger a manual sync for a connection."""
    try:
        conn_uuid = UUID(connection_id)
        conn = await db.execute(select(Connection).where(Connection.id == conn_uuid))
        connection = conn.scalar_one_or_none()
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        if not await get_company_owned(db, connection.company_id, user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        sync_log = await sync_connection(db, connection)
        log_event(str(user.id), "sync_connection", connection_id, sync_log.status.value)
        return {
            "sync_id": str(sync_log.id), "status": sync_log.status.value,
            "items_fetched": sync_log.items_fetched, "items_imported": sync_log.items_imported,
            "items_updated": sync_log.items_updated, "items_failed": sync_log.items_failed,
            "error": sync_log.error_message,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{connection_id}/upload-csv")
async def upload_csv(
    connection_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Upload a CSV file to a CSV import connection."""
    conn = await db.execute(select(Connection).where(Connection.id == UUID(connection_id)))
    connection = conn.scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if not await get_company_owned(db, connection.company_id, user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    if connection.connection_type != ConnectionType.CSV_IMPORT:
        raise HTTPException(status_code=400, detail="Only CSV import connections accept file uploads")

    content = await file.read()
    items = CSVConnector.parse_csv_bytes(content)
    current_config = dict(connection.config) if connection.config else {}
    current_config["csv_data"] = items
    current_config["filename"] = file.filename or "upload.csv"
    connection.config = current_config
    return {"items_parsed": len(items), "preview": items[:5]}


@router.get("/{connection_id}/sync-history")
async def get_sync_history(
    connection_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Get sync history for a connection."""
    conn_uuid = UUID(connection_id)
    conn = await db.execute(select(Connection).where(Connection.id == conn_uuid))
    connection = conn.scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if not await get_company_owned(db, connection.company_id, user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    logs = await db.execute(
        select(SyncLog).where(SyncLog.connection_id == conn_uuid)
        .order_by(SyncLog.started_at.desc()).limit(limit)
    )
    return [
        {"id": str(l.id), "status": l.status.value, "items_fetched": l.items_fetched,
         "items_imported": l.items_imported, "items_updated": l.items_updated,
         "items_failed": l.items_failed, "error": l.error_message,
         "started_at": l.started_at, "completed_at": l.completed_at}
        for l in logs.scalars().all()
    ]


@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Delete a connection."""
    conn = await db.execute(select(Connection).where(Connection.id == UUID(connection_id)))
    connection = conn.scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if not await get_company_owned(db, connection.company_id, user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    await db.delete(connection)
    log_event(str(user.id), "delete_connection", connection_id, "success")
    return {"deleted": True}
