"""Company service."""

import re
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User


def generate_slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower().strip())
    slug = slug.strip("-")
    return slug or f"company-{uuid4().hex[:8]}"


async def create_company(db: AsyncSession, name: str, industry: str | None, user: User) -> Company:
    slug = generate_slug(name)
    company = Company(name=name, slug=slug, industry=industry, owner_id=user.id)
    db.add(company)
    await db.flush()
    await db.refresh(company)
    return company


async def get_companies(db: AsyncSession, user: User):
    """Only return companies owned by this user."""
    result = await db.execute(
        select(Company)
        .where(Company.owner_id == user.id, Company.is_active.is_(True))
        .order_by(Company.created_at.desc())
    )
    return result.scalars().all()


async def get_company_by_id(db: AsyncSession, company_id: UUID, user_id: UUID) -> Company | None:
    """Only return company if owned by this user."""
    result = await db.execute(
        select(Company).where(Company.id == company_id, Company.owner_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_company(db: AsyncSession, company: Company, data: dict) -> Company:
    for key, value in data.items():
        if value is not None and key in ("name", "industry", "is_active"):
            setattr(company, key, value)
    await db.flush()
    await db.refresh(company)
    return company


async def delete_company(db: AsyncSession, company: Company) -> Company:
    company.is_active = False
    await db.flush()
    await db.refresh(company)
    return company
