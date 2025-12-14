"""
Trigger Detection API routes.

Endpoints for detecting and scanning market triggers.
"""

from typing import List, Optional
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException

from ...core.trigger_detector import TriggerDetector, DEFAULT_WATCHLIST
from ...core.triggers import TriggerType

router = APIRouter(prefix="/api/triggers", tags=["Triggers"])


class TriggerScanRequest(BaseModel):
    """Request model for trigger scan."""
    symbols: Optional[List[str]] = None  # None = use default watchlist
    trigger_types: Optional[List[str]] = None  # None = all triggers


class TriggeredAssetResponse(BaseModel):
    """Response model for a triggered asset."""
    symbol: str
    trigger_type: str
    trigger_reason: str
    priority: str
    relevant_phantoms: List[str]
    detected_at: str
    metrics: dict


class TriggerScanResponse(BaseModel):
    """Response model for trigger scan."""
    total_triggers: int
    symbols_scanned: int
    by_type: dict
    by_priority: dict
    triggered_assets: List[TriggeredAssetResponse]


@router.post("/scan", response_model=TriggerScanResponse)
async def scan_for_triggers(request: TriggerScanRequest) -> TriggerScanResponse:
    """
    Scan symbols for trigger conditions.

    Returns assets that meet trigger criteria for phantom analysis.
    """
    symbols = request.symbols or DEFAULT_WATCHLIST

    if len(symbols) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 symbols per scan")

    detector = TriggerDetector()

    try:
        triggered = await detector.scan_watchlist(
            symbols=symbols,
            trigger_types=request.trigger_types,
        )

        summary = await detector.get_trigger_summary(triggered)

        return TriggerScanResponse(
            total_triggers=summary["total_triggers"],
            symbols_scanned=len(symbols),
            by_type=summary["by_type"],
            by_priority=summary["by_priority"],
            triggered_assets=[
                TriggeredAssetResponse(
                    symbol=t.symbol,
                    trigger_type=t.trigger_type.value,
                    trigger_reason=t.trigger_reason,
                    priority=t.priority,
                    relevant_phantoms=t.relevant_phantoms,
                    detected_at=t.detected_at.isoformat(),
                    metrics=t.metrics,
                )
                for t in triggered
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("/types", response_model=List[dict])
async def get_trigger_types() -> List[dict]:
    """Get available trigger types and descriptions."""
    return [
        {
            "type": TriggerType.MASSIVE_DRAWDOWN.value,
            "description": "Price down 20%+ with stable fundamentals",
            "category": "statistical",
            "relevant_phantoms": ["burry", "buffett", "ackman"],
        },
        {
            "type": TriggerType.VALUATION_DISLOCATION.value,
            "description": "PE ratio below 50% of 5-year average",
            "category": "statistical",
            "relevant_phantoms": ["burry", "buffett", "munger"],
        },
        {
            "type": TriggerType.SHORT_SQUEEZE_SETUP.value,
            "description": "High short interest with quality fundamentals",
            "category": "statistical",
            "relevant_phantoms": ["burry", "ackman"],
        },
        {
            "type": TriggerType.CRISIS_OPPORTUNITY.value,
            "description": "Sector down but company moat intact",
            "category": "quality",
            "relevant_phantoms": ["buffett", "munger", "ackman"],
        },
        {
            "type": TriggerType.MOAT_EXPANSION.value,
            "description": "Signs of strengthening competitive advantage",
            "category": "quality",
            "relevant_phantoms": ["buffett", "munger", "lynch"],
        },
        {
            "type": TriggerType.REGIME_CHANGE.value,
            "description": "Fed policy pivot or inflation trend reversal",
            "category": "macro",
            "relevant_phantoms": ["dalio", "burry", "buffett"],
        },
        {
            "type": TriggerType.CYCLE_TURN.value,
            "description": "Economic cycle bottoming or topping",
            "category": "macro",
            "relevant_phantoms": ["dalio", "buffett", "lynch"],
        },
    ]


@router.get("/watchlist", response_model=List[str])
async def get_default_watchlist() -> List[str]:
    """Get the default watchlist for scanning."""
    return DEFAULT_WATCHLIST
