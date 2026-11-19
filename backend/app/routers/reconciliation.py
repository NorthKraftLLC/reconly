"""Reconciliation router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.reconciliation import CreateReconciliation, DiscrepancyResponse, ReconciliationResponse
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
    rec = await create_reconciliation(db, data.company_id, data.name, data.source_data or {}, user.id)
    rec = await run_reconciliation(db, rec)
    return rec


@router.get("/", response_model=list[ReconciliationResponse])
async def rec_list(
    company_id: UUID, db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)
):
    return await list_reconciliations(db, company_id)


@router.get("/{rec_id}", response_model=ReconciliationResponse)
async def get(rec_id: UUID, db: AsyncSession = Depends(get_async_session)):
    rec = await get_reconciliation(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return rec


@router.get("/{rec_id}/discrepancies", response_model=list[DiscrepancyResponse])
async def discrepancies(rec_id: UUID, db: AsyncSession = Depends(get_async_session)):
    rec = await get_reconciliation(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return await get_discrepancies(db, rec_id)
