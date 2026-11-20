"""Reconciliation router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.reconciliation import CreateReconciliation, DiscrepancyResponse, ReconciliationResponse
from app.services.inventory_service import get_company_owned
from app.services.reconciliation_service import (
    create_reconciliation,
    get_discrepancies,
    get_reconciliation,
    list_reconciliations,
    run_reconciliation,
)

router = APIRouter(prefix="/reconciliations", tags=["reconciliations"])


@router.post("/", response_model=ReconciliationResponse)
async def create(
    data: CreateReconciliation, db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)
):
    company = await get_company_owned(db, data.company_id, user.id)
    if not company:
        raise HTTPException(status_code=403, detail="Company not found or access denied")
    rec = await create_reconciliation(db, data.company_id, data.name, data.source_data or {}, user.id)
    rec = await run_reconciliation(db, rec)
    return rec


@router.get("/", response_model=list[ReconciliationResponse])
async def rec_list(
    company_id: UUID, db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)
):
    company = await get_company_owned(db, company_id, user.id)
    if not company:
        raise HTTPException(status_code=403, detail="Company not found or access denied")
    return await list_reconciliations(db, company_id)


@router.get("/{rec_id}", response_model=ReconciliationResponse)
async def get(rec_id: UUID, db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    rec = await get_reconciliation(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    # Verify user owns the company this reconciliation belongs to
    company = await get_company_owned(db, rec.company_id, user.id)
    if not company:
        raise HTTPException(status_code=403, detail="Access denied")
    return rec


@router.get("/{rec_id}/discrepancies", response_model=list[DiscrepancyResponse])
async def discrepancies(rec_id: UUID, db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    rec = await get_reconciliation(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    # Verify user owns the company
    company = await get_company_owned(db, rec.company_id, user.id)
    if not company:
        raise HTTPException(status_code=403, detail="Access denied")
    return await get_discrepancies(db, rec_id)
