"""V1 API router - mounts all sub-routers."""

from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.companies import router as companies_router
from app.routers.inventory import router as inventory_router
from app.routers.reconciliation import router as reconciliation_router
from app.routers.reports import router as reports_router
from app.routers.payments import router as payments_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router, tags=["auth"])
v1_router.include_router(companies_router, tags=["companies"])
v1_router.include_router(inventory_router, tags=["inventory"])
v1_router.include_router(reconciliation_router, tags=["reconciliations"])
v1_router.include_router(reports_router, tags=["reports"])
v1_router.include_router(payments_router, tags=["payments"])
