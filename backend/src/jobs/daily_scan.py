"""
Daily scan job implementation.

Automated morning scan for opportunities:
1. Screen watchlist for triggers
2. Enrich triggered assets with market data
3. Run phantom council analysis
4. Score opportunities
5. Store top results in database
"""

import logging
import asyncio
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..config import get_settings
from ..core.trigger_detector import TriggerDetector, DEFAULT_WATCHLIST
from ..core.triggers import TriggeredAsset
from ..core.opportunity_scorer import OpportunityScorer
from ..services.perplexity_service import fetch_market_context, format_context_for_phantom
from ..services.finnhub_service import get_financial_data, format_financial_context
from ..services.anthropic_service import analyze_with_council, synthesize_council
from ..services.database import SessionLocal
from ..services.opportunity_service import OpportunityService
from ..models.opportunity import OpportunityCreate

logger = logging.getLogger(__name__)
settings = get_settings()


async def run_daily_scan(
    watchlist: Optional[List[str]] = None,
    min_score: float = 6.0,
    max_opportunities: int = 20,
) -> dict:
    """
    Run the automated daily opportunity scan.

    This is the main scheduled job that runs before market open.

    Args:
        watchlist: Optional custom watchlist (defaults to DEFAULT_WATCHLIST)
        min_score: Minimum score to store opportunity (default 6.0)
        max_opportunities: Maximum opportunities to store (default 20)

    Returns:
        Summary of scan results
    """
    start_time = datetime.utcnow()
    logger.info("Starting daily opportunity scan...")

    watchlist = watchlist or DEFAULT_WATCHLIST
    scan_id = str(uuid4())

    try:
        # 1. Detect triggers
        detector = TriggerDetector()
        triggered_assets = await detector.scan_watchlist(watchlist)
        logger.info(f"Found {len(triggered_assets)} triggered assets")

        if not triggered_assets:
            logger.info("No triggers detected. Scan complete.")
            return {
                "success": True,
                "scan_id": scan_id,
                "triggered_count": 0,
                "analyzed_count": 0,
                "stored_count": 0,
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
            }

        # 2. Analyze triggered assets
        opportunities = []
        scorer = OpportunityScorer()

        for asset in triggered_assets[:max_opportunities]:  # Limit to prevent API overload
            try:
                result = await _analyze_triggered_asset(asset, scorer)
                if result and result["score"] >= min_score:
                    opportunities.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze {asset.symbol}: {e}")
                continue

        logger.info(f"Analyzed {len(opportunities)} opportunities with score >= {min_score}")

        # 3. Sort and store top opportunities
        opportunities.sort(key=lambda x: x["score"], reverse=True)
        top_opportunities = opportunities[:max_opportunities]

        stored_count = 0
        if top_opportunities:
            stored_count = await _store_opportunities(top_opportunities, scan_id)

        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Daily scan complete. Stored {stored_count} opportunities in {duration:.1f}s")

        return {
            "success": True,
            "scan_id": scan_id,
            "triggered_count": len(triggered_assets),
            "analyzed_count": len(opportunities),
            "stored_count": stored_count,
            "top_score": top_opportunities[0]["score"] if top_opportunities else 0,
            "duration_seconds": duration,
        }

    except Exception as e:
        logger.error(f"Daily scan failed: {e}")
        return {
            "success": False,
            "scan_id": scan_id,
            "error": str(e),
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
        }


async def run_watchlist_scan(
    symbols: List[str],
    include_context: bool = True,
) -> dict:
    """
    Run a manual scan on a specific watchlist.

    Similar to daily scan but for on-demand use.
    """
    start_time = datetime.utcnow()
    scan_id = str(uuid4())

    logger.info(f"Starting watchlist scan for {len(symbols)} symbols...")

    opportunities = []
    scorer = OpportunityScorer()

    for symbol in symbols:
        try:
            result = await _analyze_symbol(symbol, include_context, scorer)
            if result:
                opportunities.append(result)
        except Exception as e:
            logger.error(f"Failed to analyze {symbol}: {e}")
            continue

    # Sort by score
    opportunities.sort(key=lambda x: x["score"], reverse=True)

    duration = (datetime.utcnow() - start_time).total_seconds()

    return {
        "success": True,
        "scan_id": scan_id,
        "symbols_scanned": len(symbols),
        "opportunities_found": len(opportunities),
        "opportunities": opportunities,
        "duration_seconds": duration,
    }


async def run_price_update():
    """
    Update current prices for recent opportunities.

    Scheduled job to track performance of stored opportunities.
    """
    from ..services.finnhub_service import batch_get_quotes

    logger.info("Starting price update job...")

    try:
        db = SessionLocal()
        service = OpportunityService(db)

        # Get recent opportunities with prices
        opportunities = service.get_recent(limit=100, days=7)
        opportunities_with_price = [o for o in opportunities if o.price_at_scan]

        if not opportunities_with_price:
            logger.info("No opportunities with price data to update")
            db.close()
            return

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
        db.close()

        logger.info(f"Updated prices for {updated_count} opportunities")

    except Exception as e:
        logger.error(f"Price update failed: {e}")


async def _analyze_triggered_asset(
    asset: TriggeredAsset,
    scorer: OpportunityScorer,
) -> Optional[dict]:
    """Analyze a single triggered asset."""
    symbol = asset.symbol

    # Fetch market context
    context_str = None
    try:
        # Get Perplexity context
        context = await fetch_market_context(symbol)
        context_str = format_context_for_phantom(context)

        # Get financial context
        financial_data = await get_financial_data(symbol)
        financial_context = format_financial_context(financial_data)

        if financial_context:
            context_str = f"{context_str}\n\n{financial_context}" if context_str else financial_context

    except Exception as e:
        logger.warning(f"Context fetch failed for {symbol}: {e}")

    # Run council analysis (prefer relevant phantoms for this trigger)
    analyses = await analyze_with_council(
        asset=symbol,
        context=context_str,
        phantom_ids=asset.relevant_phantoms if len(asset.relevant_phantoms) >= 3 else None,
    )

    if not analyses:
        return None

    # Synthesize
    synthesis = await synthesize_council(symbol, analyses)

    # Score with trigger context
    score_result = scorer.score(
        analyses=analyses,
        synthesis=synthesis,
        trigger_type=asset.trigger_type.value,
    )

    return {
        "symbol": symbol,
        "score": score_result.score,
        "trigger_type": asset.trigger_type.value,
        "trigger_reason": asset.trigger_reason,
        "consensus_position": synthesis.get("consensus_position"),
        "consensus_strength": synthesis.get("consensus_strength"),
        "key_insight": score_result.explanation,
        "patterns_detected": [p.pattern.value for p in score_result.patterns_detected if p.detected],
        "action_items": score_result.action_items,
        "risk_factors": score_result.risk_factors,
        "phantom_breakdown": score_result.phantom_breakdown,
        "analyses": analyses,
    }


async def _analyze_symbol(
    symbol: str,
    include_context: bool,
    scorer: OpportunityScorer,
) -> Optional[dict]:
    """Analyze a single symbol without trigger context."""
    # Fetch market context
    context_str = None
    if include_context:
        try:
            context = await fetch_market_context(symbol)
            context_str = format_context_for_phantom(context)

            financial_data = await get_financial_data(symbol)
            financial_context = format_financial_context(financial_data)

            if financial_context:
                context_str = f"{context_str}\n\n{financial_context}" if context_str else financial_context

        except Exception as e:
            logger.warning(f"Context fetch failed for {symbol}: {e}")

    # Run council analysis
    analyses = await analyze_with_council(asset=symbol, context=context_str)

    if not analyses:
        return None

    # Synthesize
    synthesis = await synthesize_council(symbol, analyses)

    # Score
    score_result = scorer.score(analyses=analyses, synthesis=synthesis)

    return {
        "symbol": symbol,
        "score": score_result.score,
        "consensus_position": synthesis.get("consensus_position"),
        "consensus_strength": synthesis.get("consensus_strength"),
        "key_insight": score_result.explanation,
        "patterns_detected": [p.pattern.value for p in score_result.patterns_detected if p.detected],
        "action_items": score_result.action_items,
        "risk_factors": score_result.risk_factors,
        "phantom_breakdown": score_result.phantom_breakdown,
    }


async def _store_opportunities(
    opportunities: List[dict],
    scan_id: str,
) -> int:
    """Store opportunities in database."""
    db = SessionLocal()
    service = OpportunityService(db)

    stored = 0
    for opp in opportunities:
        try:
            # Get high conviction count from phantom breakdown
            high_conviction_count = sum(
                1 for p in opp.get("phantom_breakdown", {}).values()
                if p.get("conviction") == "high"
            )

            # Get bullish/bearish phantoms
            bullish = [k for k, v in opp.get("phantom_breakdown", {}).items() if v.get("position") == "bullish"]
            bearish = [k for k, v in opp.get("phantom_breakdown", {}).items() if v.get("position") in ["bearish", "avoid"]]

            create_data = OpportunityCreate(
                symbol=opp["symbol"],
                scan_id=scan_id,
                opportunity_score=opp["score"],
                consensus_position=opp.get("consensus_position"),
                consensus_strength=opp.get("consensus_strength"),
                high_conviction_count=high_conviction_count,
                total_phantoms=len(opp.get("phantom_breakdown", {})),
                bullish_phantoms=bullish,
                bearish_phantoms=bearish,
                key_insight=opp["key_insight"],
                market_context=opp.get("trigger_reason"),
            )

            service.create(create_data)
            stored += 1

        except Exception as e:
            logger.error(f"Failed to store opportunity {opp['symbol']}: {e}")

    db.commit()
    db.close()

    return stored
