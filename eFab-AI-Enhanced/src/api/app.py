"""
FastAPI Application for eFab AI Enhanced
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.config import settings
from src.api.routers import auth, planning, inventory, forecasting, analytics
from src.database.connection import init_db, close_db
from src.api.middleware.logging import LoggingMiddleware
from src.api.middleware.error_handler import error_handler_middleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered supply chain optimization platform for textile manufacturing",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.middleware("http")(error_handler_middleware)
app.add_middleware(LoggingMiddleware)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.env,
        "timestamp": time.time()
    }


# Ready check endpoint
@app.get("/ready", tags=["Health"])
async def readiness_check() -> Dict[str, Any]:
    """Readiness check endpoint"""
    # TODO: Add actual readiness checks (DB, Redis, etc.)
    return {
        "status": "ready",
        "services": {
            "database": "connected",
            "redis": "connected",
            "ml_models": "loaded"
        }
    }


# Include routers
app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["Authentication"])
app.include_router(planning.router, prefix=f"{settings.api_prefix}/planning", tags=["Planning"])
app.include_router(inventory.router, prefix=f"{settings.api_prefix}/inventory", tags=["Inventory"])
app.include_router(forecasting.router, prefix=f"{settings.api_prefix}/forecasting", tags=["Forecasting"])
app.include_router(analytics.router, prefix=f"{settings.api_prefix}/analytics", tags=["Analytics"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )