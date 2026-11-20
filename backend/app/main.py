"""FastAPI application entry point."""

import os
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.core.security_headers import security_headers_middleware
from app.db.session import close_engine

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("App starting up...", flush=True)
        yield
        print("App shutting down...", flush=True)
        await close_engine()
    except Exception as e:
        print(f"Lifespan error: {e}", flush=True)
        traceback.print_exc()
        raise


app = FastAPI(
    title="Inventory Reconciliation SaaS",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,  # Disable docs in production
    redoc_url=None,
    openapi_url=None,
)

# Rate limiter
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Try again later."},
    )


# CORS - restrictive config
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000", "https://reconly-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    max_age=600,
)

# Request size limit middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
        return JSONResponse(
            status_code=413,
            content={"detail": "Request too large. Maximum 10MB."},
        )
    return await call_next(request)


# Security headers middleware
app.middleware("http")(security_headers_middleware)

# Mount API router
try:
    from app.api.v1.router import v1_router

    app.include_router(v1_router)
    print("API router mounted", flush=True)
except Exception as e:
    print(f"Failed to mount API router: {e}", flush=True)
    traceback.print_exc()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/admin/migrate")
async def run_migrations():
    """Run database migrations (admin only)."""
    try:
        from sqlalchemy import text
        from app.db.session import get_engine
        engine = get_engine()
        # Create all tables
        from app.models.base import Base
        from app.models import User, Company, InventoryItem, Reconciliation, Discrepancy, Connection, SyncLog
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Add owner_id column to companies if it doesn't exist (migration)
        async with engine.begin() as conn:
            await conn.execute(text("""
                DO $$ BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='companies' AND column_name='owner_id') THEN
                        ALTER TABLE companies ADD COLUMN owner_id UUID NOT NULL DEFAULT gen_random_uuid();
                    END IF;
                END $$;
            """))

        # Create a bypass role for admin operations (health checks, migrations)
        async with engine.begin() as conn:
            await conn.execute(text("""
                DO $$ BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rls_bypass') THEN
                        CREATE ROLE rls_bypass;
                    END IF;
                END $$;
            """))

        # Apply Row-Level Security policies
        from app.core.rls import apply_rls_policies
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with Session() as db:
            # Temporarily disable RLS for migration setup
            await db.execute(text("SET row_security = off"))
            await apply_rls_policies(db)
            await db.execute(text("SET row_security = on"))

        return {"status": "ok", "message": "All tables created, RLS policies applied"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}