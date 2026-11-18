"""Companies router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.company import CreateCompany, UpdateCompany, CompanyResponse
from app.services.company_service import create_company, get_companies, get_company_by_id, update_company, delete_company
from app.dependencies import get_current_user
from app.models.user import User
from app.core.audit import log_event

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyResponse)
async def create(data: CreateCompany, db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    company = await create_company(db, data.name, data.industry, user)
    log_event(str(user.id), "create_company", str(company.id), "success")
    return company


@router.get("/", response_model=list[CompanyResponse])
async def list_companies(db: AsyncSession = Depends(get_async_session), user: User = Depends(get_current_user)):
    companies = await get_companies(db, user)
    return companies


@router.get("/{id}", response_model=CompanyResponse)
async def get(id: UUID, db: AsyncSession = Depends(get_async_session)):
    company = await get_company_by_id(db, id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/{id}", response_model=CompanyResponse)
async def patch(id: UUID, data: UpdateCompany, db: AsyncSession = Depends(get_async_session)):
    company = await get_company_by_id(db, id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    updated = await update_company(db, company, data.model_dump(exclude_unset=True))
    log_event("system", "update_company", str(id), "success")
    return updated


@router.delete("/{id}")
async def delete(id: UUID, db: AsyncSession = Depends(get_async_session)):
    company = await get_company_by_id(db, id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    await delete_company(db, company)
    log_event("system", "delete_company", str(id), "success")
    return {"status": "deleted"}
