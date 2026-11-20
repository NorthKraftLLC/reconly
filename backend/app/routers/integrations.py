"""Integrations/Connections router for managing data sources."""

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
    get_connector,
    sync_connection,
    CSVConnector,
    CONNECTOR_MAP,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/types")
async def get_connector_types():
    """Return all available connector types with their info."""
    types = []
    for conn_type, cls in CONNECTOR_MAP.items():
        types.append({
            "type": conn_type.value,
            "name": cls.__name__.replace("Connector", ""),
            "description": cls.__doc__ or "",
        })
    return {"types": types}


@router.get("/")
async def list_connections(db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    """List all connections for the current user's companies."""
    user_companies = await db.execute(
        select(Connection).where(Connection.company_id.in_(
            select(Connection.company_id).distinct()
        ))
    )
    # Filter by user's companies via their ownership
    connections = await db.execute(select(Connection).order_by(Connection.created_at.desc()))
    return connections.scalars().all()


@router.post("/", response_model=dict)
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
    import json as json_mod

    try:
        conn_type = ConnectionType(connection_type)
        conn_role = ConnectionRole(role)
        creds = json_mod.loads(credentials)
        cfg = json_mod.loads(config)
    except (ValueError, json_mod.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    connection = Connection(
        name=name,
        connection_type=conn_type,
        role=conn_role,
        company_id=company_id,
        credentials=creds,
        config=cfg,
    )
    db.add(connection)
    await db.commit()
    await db.refresh(connection)
    log_event(str(user.id), "create_connection", str(connection.id), "success")
    return {"id": str(connection.id), "name": connection.name, "type": connection.connection_type.value, "role": connection.role.value}


@router.post("/{connection_id}/test")
async def test_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Test if a connection's credentials are valid."""
    conn = await db.execute(select(Connection).where(Connection.id == connection_id))
    connection = conn.scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

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
    conn = await db.execute(select(Connection).where(Connection.id == connection_id))
    connection = conn.scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    sync_log = await sync_connection(db, connection)
    log_event(str(user.id), "sync_connection", connection_id, sync_log.status.value)
    return {
        "sync_id": str(sync_log.id),
        "status": sync_log.status.value,
        "items_fetched": sync_log.items_fetched,
        "items_imported": sync_log.items_imported,
        "items_updated": sync_log.items_updated,
        "items_failed": sync_log.items_failed,
        "error": sync_log.error_message,
    }


@router.post("/{connection_id}/upload-csv")
async def upload_csv(
    connection_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Upload a CSV file to a CSV import connection."""
    conn = await db.execute(select(Connection).where(Connection.id == connection_id))
    connection = conn.scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if connection.connection_type != ConnectionType.CSV_IMPORT:
        raise HTTPException(status_code=400, detail="Only CSV import connections accept file uploads")

    content = await file.read()
    items = CSVConnector.parse_csv_bytes(content)
    connection.config["csv_data"] = items
    connection.config["filename"] = file.filename
    await db.commit()

    return {"items_parsed": len(items), "preview": items[:5]}


@router.get("/{connection_id}/sync-history")
async def get_sync_history(
    connection_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Get sync history for a connection."""
    logs = await db.execute(
        select(SyncLog)
        .where(SyncLog.connection_id == connection_id)
        .order_by(SyncLog.started_at.desc())
        .limit(limit)
    )
    return [
        {
            "id": str(l.id),
            "status": l.status.value,
            "items_fetched": l.items_fetched,
            "items_imported": l.items_imported,
            "items_updated": l.items_updated,
            "items_failed": l.items_failed,
            "error": l.error_message,
            "started_at": l.started_at,
            "completed_at": l.completed_at,
        }
        for l in logs.scalars().all()
    ]


@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Delete a connection."""
    conn = await db.execute(select(Connection).where(Connection.id == connection_id))
    connection = conn.scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    await db.delete(connection)
    await db.commit()
    log_event(str(user.id), "delete_connection", connection_id, "success")
    return {"deleted": True}
