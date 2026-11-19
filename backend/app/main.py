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
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
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
    import subprocess
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "DATABASE_URL": settings.DATABASE_URL}
        )
        return {"status": "ok" if result.returncode == 0 else "failed", "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"status": "error", "detail": str(e)}