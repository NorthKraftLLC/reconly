"""Reconciliation service."""

from datetime import UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.discrepancy import Discrepancy
from app.models.reconciliation import Reconciliation, ReconciliationStatus
from app.services.matching_service import reconcile_sources


async def create_reconciliation(
    db: AsyncSession, company_id: UUID, name: str, source_data: dict, created_by: UUID
) -> Reconciliation:
    rec = Reconciliation(
        company_id=company_id,
        name=name,
        status=ReconciliationStatus.PENDING.value,
        source_data=source_data,
        created_by=created_by,
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


async def run_reconciliation(db: AsyncSession, rec: Reconciliation) -> Reconciliation:
    rec.status = ReconciliationStatus.IN_PROGRESS.value
    await db.commit()

    results = reconcile_sources(rec.source_data or {})
    rec.total_items = results["total_items"]
    rec.matched_items = results["matched_items"]
    rec.discrepancies_found = results["discrepancies_found"]
    rec.status = ReconciliationStatus.COMPLETED.value

    for disc in results["discrepancies"]:
        d = Discrepancy(
            reconciliation_id=rec.id,
            company_id=rec.company_id,
            item_name=disc["item_name"],
            item_sku=disc.get("item_sku"),
            system_quantity=disc["system_quantity"],
            source_quantity=disc["source_quantity"],
            quantity_difference=disc["quantity_difference"],
            discrepancy_type=disc["discrepancy_type"],
            severity=disc["severity"],
            explanation=disc["explanation"],
        )
        db.add(d)
    await db.commit()
    return rec


async def list_reconciliations(db: AsyncSession, company_id: UUID):
    result = await db.execute(
        select(Reconciliation).where(Reconciliation.company_id == company_id).order_by(Reconciliation.created_at.desc())
    )
    return result.scalars().all()


async def get_reconciliation(db: AsyncSession, rec_id) -> Reconciliation | None:
    result = await db.execute(select(Reconciliation).where(Reconciliation.id == rec_id))
    return result.scalar_one_or_none()


async def get_discrepancies(db: AsyncSession, rec_id):
    result = await db.execute(
        select(Discrepancy).where(Discrepancy.reconciliation_id == rec_id).order_by(Discrepancy.created_at.desc())
    )
    return result.scalars().all()


async def resolve_discrepancy(db: AsyncSession, disc_id, user_id: UUID, notes: str | None = None):
    from datetime import datetime

    result = await db.execute(select(Discrepancy).where(Discrepancy.id == disc_id))
    disc = result.scalar_one_or_none()
    if not disc:
        raise ValueError("Discrepancy not found")
    disc.resolved = True
    disc.resolved_by = user_id
    disc.resolved_at = str(datetime.now(UTC))
    disc.reviewer_notes = notes
    await db.commit()
    return disc
