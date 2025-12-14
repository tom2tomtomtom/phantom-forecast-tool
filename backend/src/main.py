"""
Main FastAPI application for the Phantom Forecast Tool API.

Entry point for the REST API that provides:
- Phantom investor analysis endpoints
- Market data integration
- Council synthesis views
"""

import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .services.database import init_db, close_db
from .api.routes import phantom_router, quick_scan_router, opportunities_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    init_db()
    yield
    # Shutdown
    print("Shutting down API...")
    close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered market intelligence through competing investor phantom personas",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    """Add X-Process-Time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc) -> JSONResponse:
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "message": "The requested resource was not found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc) -> JSONResponse:
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "An internal server error occurred"},
    )


# Include routers
app.include_router(phantom_router, prefix="/api")
app.include_router(quick_scan_router)  # Already has /api/scan prefix
app.include_router(opportunities_router)  # Already has /api/opportunities prefix


# Health endpoint
@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Check if the API is healthy and running.",
)
async def health_check() -> dict:
    """Return health status."""
    return {
        "status": "healthy",
        "service": "phantom-forecast-api",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Root endpoint
@app.get(
    "/",
    tags=["health"],
    summary="API Information",
    description="Get basic information about the API.",
)
async def root() -> dict:
    """Return API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Phantom Forecast Tool - Pluralistic strategic intelligence",
        "documentation": "/docs",
        "health": "/health",
    }


def main():
    """Run the API server."""
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
    )


if __name__ == "__main__":
    main()
