"""
Opportunities API routes.

Endpoints for saving, retrieving, and managing opportunity scan results.
"""

from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...services.database import get_db
from ...services.opportunity_service import OpportunityService
from ...services.finnhub_service import batch_get_quotes
from ...models.opportunity import OpportunityCreate, OpportunityResponse

router = APIRouter(prefix="/api/opportunities", tags=["Opportunities"])


@router.post("/save", response_model=dict)
async def save_opportunities(
    opportunities: List[OpportunityCreate],
    db: Session = Depends(get_db)
) -> dict:
    """
    Save opportunities from a scan to the database.

    Accepts a list of opportunities and saves them with a shared scan_id.
    """
    if not opportunities:
        raise HTTPException(status_code=400, detail="No opportunities provided")

    service = OpportunityService(db)
    scan_id = str(uuid4())

    try:
        saved = service.save_batch(opportunities, scan_id=scan_id)
        return {
            "success": True,
            "scan_id": scan_id,
            "saved_count": len(saved),
            "message": f"Saved {len(saved)} opportunities"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save: {str(e)}")


@router.get("/recent", response_model=List[OpportunityResponse])
async def get_recent_opportunities(
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(0.0, ge=0, le=10),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
) -> List[OpportunityResponse]:
    """Get recent opportunities with optional filters."""
    service = OpportunityService(db)
    opportunities = service.get_recent(limit=limit, min_score=min_score, days=days)

    return [OpportunityResponse(**opp.to_dict()) for opp in opportunities]


@router.get("/top", response_model=List[OpportunityResponse])
async def get_top_opportunities(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
) -> List[OpportunityResponse]:
    """Get top scoring opportunities."""
    service = OpportunityService(db)
    opportunities = service.get_top_opportunities(limit=limit, days=days)

    return [OpportunityResponse(**opp.to_dict()) for opp in opportunities]


@router.get("/symbol/{symbol}", response_model=List[OpportunityResponse])
async def get_symbol_history(
    symbol: str,
    limit: int = Query(10, ge=1, le=50),
    days: Optional[int] = Query(None, ge=1, le=365),
    db: Session = Depends(get_db)
) -> List[OpportunityResponse]:
    """Get historical opportunities for a specific symbol."""
    service = OpportunityService(db)
    opportunities = service.get_by_symbol(symbol, limit=limit, days=days)

    return [OpportunityResponse(**opp.to_dict()) for opp in opportunities]


@router.get("/scan/{scan_id}", response_model=List[OpportunityResponse])
async def get_scan_results(
    scan_id: str,
    db: Session = Depends(get_db)
) -> List[OpportunityResponse]:
    """Get all opportunities from a specific scan."""
    service = OpportunityService(db)
    opportunities = service.get_by_scan_id(scan_id)

    if not opportunities:
        raise HTTPException(status_code=404, detail="Scan not found")

    return [OpportunityResponse(**opp.to_dict()) for opp in opportunities]


@router.get("/consensus/{position}", response_model=List[OpportunityResponse])
async def get_by_consensus(
    position: str,
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
) -> List[OpportunityResponse]:
    """Get opportunities by consensus position (bullish/bearish/neutral)."""
    if position not in ["bullish", "bearish", "neutral"]:
        raise HTTPException(status_code=400, detail="Position must be bullish, bearish, or neutral")

    service = OpportunityService(db)
    opportunities = service.get_by_consensus(position, limit=limit, days=days)

    return [OpportunityResponse(**opp.to_dict()) for opp in opportunities]


@router.get("/stats", response_model=dict)
async def get_opportunity_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
) -> dict:
    """Get aggregate statistics about opportunities."""
    service = OpportunityService(db)
    return service.get_stats(days=days)


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db)
) -> OpportunityResponse:
    """Get a single opportunity by ID."""
    service = OpportunityService(db)
    opportunity = service.get_by_id(opportunity_id)

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    return OpportunityResponse(**opportunity.to_dict())


@router.delete("/cleanup", response_model=dict)
async def cleanup_old_opportunities(
    days: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db)
) -> dict:
    """Delete opportunities older than specified days."""
    service = OpportunityService(db)
    deleted = service.delete_old(days=days)

    return {
        "success": True,
        "deleted_count": deleted,
        "message": f"Deleted {deleted} opportunities older than {days} days"
    }


@router.post("/update-prices", response_model=dict)
async def update_opportunity_prices(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
) -> dict:
    """
    Update current prices for recent opportunities.

    Fetches latest prices from Finnhub and calculates price change percentage
    since the opportunity was scanned.
    """
    service = OpportunityService(db)

    # Get recent opportunities that have a price_at_scan
    opportunities = service.get_recent(limit=100, days=days)
    opportunities_with_price = [o for o in opportunities if o.price_at_scan]

    if not opportunities_with_price:
        return {
            "success": True,
            "updated_count": 0,
            "message": "No opportunities with price data to update"
        }

    # Get unique symbols
    symbols = list(set(o.symbol for o in opportunities_with_price))

    # Fetch current quotes
    quotes = await batch_get_quotes(symbols)

    # Update each opportunity
    updated_count = 0
    for opp in opportunities_with_price:
        quote = quotes.get(opp.symbol.upper())
        if quote and opp.price_at_scan:
            opp.current_price = quote.current_price
            opp.price_change_pct = ((quote.current_price - opp.price_at_scan) / opp.price_at_scan) * 100
            opp.last_price_update = datetime.utcnow()
            updated_count += 1

    db.commit()

    return {
        "success": True,
        "updated_count": updated_count,
        "symbols_checked": len(symbols),
        "message": f"Updated prices for {updated_count} opportunities"
    }
