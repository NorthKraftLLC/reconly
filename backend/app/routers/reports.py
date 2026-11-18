"""Reports router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.services.reconciliation_service import get_reconciliation, get_discrepancies
from app.services.report_service import generate_pdf_report, generate_csv_report, generate_excel_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{rec_id}/pdf")
async def report_pdf(rec_id: UUID, db: AsyncSession = Depends(get_async_session)):
    rec = await get_reconciliation(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    discs = await get_discrepancies(db, rec_id)
    data = generate_pdf_report(rec, discs)
    return StreamingResponse(
        iter([data]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=reconciliation_{rec_id}.pdf"},
    )


@router.get("/{rec_id}/csv")
async def report_csv(rec_id: UUID, db: AsyncSession = Depends(get_async_session)):
    rec = await get_reconciliation(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    discs = await get_discrepancies(db, rec_id)
    data = generate_csv_report(discs)
    return StreamingResponse(
        iter([data]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=reconciliation_{rec_id}.csv"},
    )


@router.get("/{rec_id}/excel")
async def report_excel(rec_id: UUID, db: AsyncSession = Depends(get_async_session)):
    rec = await get_reconciliation(db, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    discs = await get_discrepancies(db, rec_id)
    data = generate_excel_report(rec, discs)
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=reconciliation_{rec_id}.xlsx"},
    )
