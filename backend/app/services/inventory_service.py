"""Inventory service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.inventory_item import InventoryItem


async def get_company_owned(db: AsyncSession, company_id: UUID, user_id: UUID) -> Company | None:
    result = await db.execute(select(Company).where(Company.id == company_id))
    return result.scalar_one_or_none()


async def create_item(db: AsyncSession, data) -> InventoryItem:
    item = InventoryItem(**{k: v for k, v in data.model_dump().items() if k != "company_id"})
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def create_bulk(db: AsyncSession, company_id: UUID, items: list) -> list:
    created = []
    for item_data in items:
        item_dict = {"company_id": company_id}
        if hasattr(item_data, "model_dump"):
            item_dict.update({k: v for k, v in item_data.model_dump().items() if k != "company_id"})
        else:
            item_dict.update({k: v for k, v in item_data.items() if k != "company_id"})
        item = InventoryItem(**item_dict)
        created.append(item)
    db.add_all(created)
    await db.commit()
    for item in created:
        await db.refresh(item)
    return created


async def list_items(db: AsyncSession, company_id: UUID, search: str | None = None, category: str | None = None):
    query = select(InventoryItem).where(InventoryItem.company_id == company_id)
    if search:
        query = query.where((InventoryItem.name.ilike(f"%{search}%")) | (InventoryItem.sku.ilike(f"%{search}%")))
    if category:
        query = query.where(InventoryItem.category == category)
    query = query.order_by(InventoryItem.name)
    result = await db.execute(query)
    return result.scalars().all()


async def get_item(db: AsyncSession, item_id) -> InventoryItem | None:
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    return result.scalar_one_or_none()


async def update_item(db: AsyncSession, item: InventoryItem, data) -> InventoryItem:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item: InventoryItem):
    await db.delete(item)
    await db.commit()
