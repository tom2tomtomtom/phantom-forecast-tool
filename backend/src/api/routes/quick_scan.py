"""
Quick Scan API - MVP Watchlist Scanner

This is the Quick-Win MVP implementation for Phase 2:
- Simple watchlist scanner (no trigger detection yet)
- Perplexity + Finnhub enrichment
- Basic scoring (high conviction consensus)
- Returns ranked opportunity list with price data
"""

import asyncio
from typing import List, Optional
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException

from ...services.perplexity_service import (
    fetch_market_context,
    format_context_for_phantom,
)
from ...services.finnhub_service import (
    get_quote,
    get_financial_data,
    format_financial_context,
)
from ...services.anthropic_service import (
    analyze_with_council,
    synthesize_council,
)
from ...models.phantom import Conviction, Position

router = APIRouter(prefix="/api/scan", tags=["Quick Scan"])


class QuickScanRequest(BaseModel):
    """Request model for quick watchlist scan."""
    symbols: List[str]
    include_context: bool = True  # Whether to fetch Perplexity context


class OpportunityResult(BaseModel):
    """Single opportunity result from scan."""
    symbol: str
    score: float
    consensus_position: Optional[str]
    consensus_strength: Optional[str]
    high_conviction_count: int
    total_phantoms: int
    key_insight: str
    bullish_phantoms: List[str]
    bearish_phantoms: List[str]
    market_context: Optional[str] = None
    # Price data from Finnhub
    current_price: Optional[float] = None
    price_change: Optional[float] = None
    price_change_pct: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None


class QuickScanResponse(BaseModel):
    """Response model for quick scan."""
    opportunities: List[OpportunityResult]
    symbols_scanned: int
    average_score: float


def calculate_opportunity_score(
    analyses: list,
    synthesis: dict,
) -> float:
    """
    Calculate opportunity score based on council patterns.

    Scoring logic:
    - High conviction consensus: 9-10
    - Strategic disagreement (some bullish, some bearish with high conviction): 7-8
    - Mixed signals: 5-6
    - Low conviction or unanimous avoid: 3-4
    - All uncertain: 1-2
    """
    if not analyses:
        return 0.0

    # Count positions and convictions
    high_conviction = sum(1 for a in analyses if a.conviction == Conviction.HIGH)
    bullish = sum(1 for a in analyses if a.position in [Position.BULLISH])
    bearish = sum(1 for a in analyses if a.position in [Position.BEARISH, Position.AVOID])
    neutral = sum(1 for a in analyses if a.position == Position.NEUTRAL)

    total = len(analyses)
    consensus_strength = synthesis.get("consensus_strength", "none")

    # Pattern 1: High-conviction consensus (9-10)
    if high_conviction >= 4 and consensus_strength == "strong":
        return 9.5 if high_conviction >= 5 else 9.0

    # Pattern 2: Strategic disagreement - some bullish, some bearish with conviction (7-8)
    if bullish >= 2 and bearish >= 2 and high_conviction >= 2:
        return 8.0

    # Pattern 3: Leaning consensus with some conviction (6-7)
    if (bullish >= 4 or bearish >= 4) and high_conviction >= 2:
        return 7.0

    # Pattern 4: Mixed signals but interesting (5-6)
    if high_conviction >= 1 and (bullish >= 1 and bearish >= 1):
        return 5.5

    # Pattern 5: Weak signals (3-4)
    if consensus_strength == "weak" or neutral >= 3:
        return 3.5

    # Pattern 6: All avoid or very low conviction (1-2)
    if bearish >= 5 or high_conviction == 0:
        return 2.0

    # Default
    return 4.0


async def analyze_single_symbol(
    symbol: str,
    include_context: bool,
) -> Optional[OpportunityResult]:
    """Analyze a single symbol - used for parallel processing."""
    symbol = symbol.upper().strip()

    # 1. Fetch market context and price data in parallel
    context_str = None
    market_summary = None
    financial_context = None
    quote_data = None

    # Prepare tasks
    context_task = None
    quote_task = get_quote(symbol)

    if include_context:
        context_task = fetch_market_context(symbol)

    # Run data fetches in parallel
    try:
        if context_task:
            context_result, quote_result = await asyncio.gather(
                context_task, quote_task, return_exceptions=True
            )
            if not isinstance(context_result, Exception):
                context_str = format_context_for_phantom(context_result)
                market_summary = context_result.summary
            if not isinstance(quote_result, Exception):
                quote_data = quote_result
        else:
            quote_result = await quote_task
            if quote_result:
                quote_data = quote_result
    except Exception as e:
        print(f"Data fetch failed for {symbol}: {e}")

    # Get financial metrics for context if we have a quote
    if quote_data:
        try:
            financial_data = await get_financial_data(symbol)
            financial_context = format_financial_context(financial_data)
            # Combine contexts
            if context_str and financial_context:
                context_str = f"{context_str}\n\n{financial_context}"
            elif financial_context:
                context_str = financial_context
        except Exception as e:
            print(f"Financial data failed for {symbol}: {e}")

    # 2. Run council analysis
    try:
        analyses = await analyze_with_council(
            asset=symbol,
            context=context_str,
        )
    except Exception as e:
        print(f"Council analysis failed for {symbol}: {e}")
        return None

    if not analyses:
        return None

    # 3. Synthesize results
    try:
        synthesis = await synthesize_council(symbol, analyses)
    except Exception as e:
        print(f"Synthesis failed for {symbol}: {e}")
        synthesis = {
            "consensus_position": None,
            "consensus_strength": "none",
            "synthesis": "Synthesis unavailable",
        }

    # 4. Calculate score
    score = calculate_opportunity_score(analyses, synthesis)

    # 5. Extract insights
    bullish_phantoms = [
        a.phantom_name for a in analyses
        if a.position == Position.BULLISH
    ]
    bearish_phantoms = [
        a.phantom_name for a in analyses
        if a.position in [Position.BEARISH, Position.AVOID]
    ]
    high_conviction_count = sum(
        1 for a in analyses if a.conviction == Conviction.HIGH
    )

    # Build key insight
    if synthesis.get("synthesis"):
        key_insight = synthesis["synthesis"]
    elif bullish_phantoms and bearish_phantoms:
        key_insight = f"Disagreement: {', '.join(bullish_phantoms[:2])} bullish vs {', '.join(bearish_phantoms[:2])} bearish"
    elif bullish_phantoms:
        key_insight = f"Bullish consensus from {', '.join(bullish_phantoms[:3])}"
    elif bearish_phantoms:
        key_insight = f"Bearish consensus from {', '.join(bearish_phantoms[:3])}"
    else:
        key_insight = "Mixed signals across council"

    return OpportunityResult(
        symbol=symbol,
        score=round(score, 1),
        consensus_position=synthesis.get("consensus_position"),
        consensus_strength=synthesis.get("consensus_strength"),
        high_conviction_count=high_conviction_count,
        total_phantoms=len(analyses),
        key_insight=key_insight,
        bullish_phantoms=bullish_phantoms,
        bearish_phantoms=bearish_phantoms,
        market_context=market_summary,
        # Price data from Finnhub
        current_price=quote_data.current_price if quote_data else None,
        price_change=quote_data.change if quote_data else None,
        price_change_pct=quote_data.percent_change if quote_data else None,
        day_high=quote_data.high if quote_data else None,
        day_low=quote_data.low if quote_data else None,
    )


@router.post("/quick", response_model=QuickScanResponse)
async def quick_opportunity_scan(request: QuickScanRequest) -> QuickScanResponse:
    """
    Quick opportunity scan on a watchlist.

    MVP version with PARALLEL processing:
    - Takes symbol list (no trigger detection)
    - Uses Perplexity for market context
    - Runs phantom council on each symbol IN PARALLEL
    - Simple scoring based on consensus patterns
    - Returns ranked list
    """
    if not request.symbols:
        raise HTTPException(status_code=400, detail="At least one symbol required")

    if len(request.symbols) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 symbols per scan")

    # Process all symbols in parallel
    tasks = [
        analyze_single_symbol(symbol, request.include_context)
        for symbol in request.symbols
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter successful results
    opportunities = []
    for result in results:
        if isinstance(result, OpportunityResult):
            opportunities.append(result)
        elif isinstance(result, Exception):
            print(f"Symbol analysis error: {result}")

    # Sort by score descending
    opportunities.sort(key=lambda x: x.score, reverse=True)

    # Calculate average score
    avg_score = (
        sum(o.score for o in opportunities) / len(opportunities)
        if opportunities else 0.0
    )

    return QuickScanResponse(
        opportunities=opportunities,
        symbols_scanned=len(request.symbols),
        average_score=round(avg_score, 1),
    )


@router.get("/health")
async def scan_health():
    """Health check for scan service."""
    return {"status": "ok", "service": "quick_scan"}
