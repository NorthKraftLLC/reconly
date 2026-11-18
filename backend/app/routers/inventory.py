"""Inventory router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.inventory_item import CreateInventoryItem, UpdateInventoryItem, InventoryResponse, BulkUploadItem
from app.services.inventory_service import get_company_owned, create_item, create_bulk, list_items, get_item, update_item, delete_item
from app.dependencies import get_current_user
from app.models.user import User
from app.core.audit import log_event

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/", response_model=InventoryResponse)
async def create(data: CreateInventoryItem, db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    company = await get_company_owned(db, data.company_id, user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    data_dict = data.model_dump()
    data_dict["company_id"] = str(data.company_id)
    from app.models.inventory_item import InventoryItem
    item = InventoryItem(**data_dict)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    log_event(str(user.id), "create_inventory", str(item.id), "success")
    return item


@router.post("/bulk", response_model=list[InventoryResponse])
async def bulk(data: list[BulkUploadItem], company_id: UUID = Query(...), db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    company = await get_company_owned(db, company_id, user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    items = await create_bulk(db, company_id, [d.model_dump() for d in data])
    return items


@router.get("/", response_model=list[InventoryResponse])
async def get_list(
    company_id: UUID = Query(...),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
    search: str | None = Query(None),
    category: str | None = Query(None),
):
    company = await get_company_owned(db, company_id, user.id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return await list_items(db, company_id, search, category)


@router.get("/{id}", response_model=InventoryResponse)
async def get(id: UUID, db: AsyncSession = Depends(get_async_session)):
    item = await get_item(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{id}", response_model=InventoryResponse)
async def patch(id: UUID, data: UpdateInventoryItem, db: AsyncSession = Depends(get_async_session)):
    item = await get_item(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return await update_item(db, item, data)


@router.delete("/{id}")
async def delete(id: UUID, db: AsyncSession = Depends(get_async_session)):
    item = await get_item(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await delete_item(db, item)
    log_event("system", "delete_inventory", str(id), "success")
    return {"status": "deleted"}
