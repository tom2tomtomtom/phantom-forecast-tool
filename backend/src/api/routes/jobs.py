"""
Job management API routes.

Endpoints for managing scheduled jobs and triggering manual scans.
"""

from typing import List, Optional
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, BackgroundTasks

from ...jobs.scheduler import get_job_status
from ...jobs.daily_scan import run_daily_scan, run_watchlist_scan, run_price_update

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


class ManualScanRequest(BaseModel):
    """Request model for manual scan."""
    symbols: Optional[List[str]] = None  # None = use default watchlist
    include_context: bool = True
    min_score: float = 6.0


class ScanResponse(BaseModel):
    """Response model for scan job."""
    success: bool
    scan_id: str
    message: str


@router.get("/status", response_model=dict)
async def get_scheduler_status() -> dict:
    """Get status of all scheduled jobs."""
    return get_job_status()


@router.post("/scan/daily", response_model=ScanResponse)
async def trigger_daily_scan(
    background_tasks: BackgroundTasks,
    min_score: float = 6.0,
) -> ScanResponse:
    """
    Manually trigger the daily opportunity scan.

    Runs in background and returns immediately.
    """
    import uuid

    scan_id = str(uuid.uuid4())

    # Run in background
    background_tasks.add_task(run_daily_scan, min_score=min_score)

    return ScanResponse(
        success=True,
        scan_id=scan_id,
        message="Daily scan started in background. Check /api/opportunities/recent for results.",
    )


@router.post("/scan/watchlist")
async def trigger_watchlist_scan(
    request: ManualScanRequest,
) -> dict:
    """
    Run a scan on a specific watchlist.

    This runs synchronously and returns results directly.
    Note: May take 1-2 minutes for larger watchlists.
    """
    if request.symbols and len(request.symbols) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 symbols per scan")

    from ...core.trigger_detector import DEFAULT_WATCHLIST

    symbols = request.symbols or DEFAULT_WATCHLIST[:10]  # Default to first 10

    try:
        result = await run_watchlist_scan(
            symbols=symbols,
            include_context=request.include_context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/update-prices", response_model=dict)
async def trigger_price_update(
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Manually trigger price update for stored opportunities.

    Runs in background.
    """
    background_tasks.add_task(run_price_update)

    return {
        "success": True,
        "message": "Price update started in background.",
    }


@router.get("/watchlist/default", response_model=List[str])
async def get_default_watchlist() -> List[str]:
    """Get the default watchlist used for scans."""
    from ...core.trigger_detector import DEFAULT_WATCHLIST
    return DEFAULT_WATCHLIST
