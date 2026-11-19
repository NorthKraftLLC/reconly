"""FastAPI application entry point."""

from contextlib import asynccontextmanager
import traceback
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.security_headers import security_headers_middleware
from app.db.session import close_engine


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
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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