"""
Main trigger detection orchestrator.

Coordinates multiple trigger types to scan for opportunities.
"""

import asyncio
from typing import List, Optional
from datetime import datetime, timedelta

from .triggers import (
    BaseTrigger,
    TriggeredAsset,
    TriggerType,
    StatisticalAnomalyTrigger,
    QualityInflectionTrigger,
    MacroShiftTrigger,
)
from ..services.finnhub_service import get_financial_data, batch_get_quotes


class TriggerDetector:
    """
    Orchestrates trigger detection across multiple trigger types.

    Scans a universe of symbols for conditions that warrant
    phantom council analysis.
    """

    def __init__(self):
        self.triggers: List[BaseTrigger] = [
            StatisticalAnomalyTrigger(),
            QualityInflectionTrigger(),
            MacroShiftTrigger(),
        ]

    async def scan_watchlist(
        self,
        symbols: List[str],
        trigger_types: Optional[List[str]] = None,
    ) -> List[TriggeredAsset]:
        """
        Scan a watchlist for trigger conditions.

        Args:
            symbols: List of ticker symbols to scan
            trigger_types: Optional filter for specific trigger types

        Returns:
            List of TriggeredAsset objects sorted by priority
        """
        if not symbols:
            return []

        # Fetch market data for all symbols in parallel
        market_data = await self._fetch_market_data(symbols)

        # Run all triggers in parallel
        all_triggered = []

        tasks = []
        for trigger in self.triggers:
            if trigger_types and trigger.name not in trigger_types:
                continue
            tasks.append(trigger.detect(symbols, market_data))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_triggered.extend(result)
            elif isinstance(result, Exception):
                print(f"Trigger detection error: {result}")

        # Sort by priority (high first) then by detection time
        priority_order = {"high": 0, "medium": 1, "low": 2}
        all_triggered.sort(key=lambda x: (priority_order.get(x.priority, 2), x.detected_at))

        return all_triggered

    async def _fetch_market_data(self, symbols: List[str]) -> dict:
        """
        Fetch market data for trigger analysis.

        Aggregates data from Finnhub and calculates derived metrics.
        """
        market_data = {}

        # Fetch quotes and financials in parallel
        tasks = [get_financial_data(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                print(f"Failed to fetch data for {symbol}: {result}")
                continue

            data = {}

            if result.quote:
                data["quote"] = result.quote
                data["current_price"] = result.quote.current_price
                data["price_change_pct"] = result.quote.percent_change

                # Estimate 30-day change from percent change (simplified)
                # In production, would fetch historical data
                data["price_change_30d"] = result.quote.percent_change * 3  # Rough estimate

            if result.financials:
                data["financials"] = result.financials
                data["pe_ratio"] = result.financials.pe_ratio
                data["roe"] = result.financials.roe
                data["beta"] = result.financials.beta
                data["dividend_yield"] = result.financials.dividend_yield
                data["week_52_high"] = result.financials.week_52_high
                data["week_52_low"] = result.financials.week_52_low

                # Estimate 5yr PE avg as current PE * 1.2 (simplified)
                if result.financials.pe_ratio:
                    data["avg_pe_5yr"] = result.financials.pe_ratio * 1.2

            if result.profile:
                data["profile"] = result.profile
                data["sector"] = result.profile.industry

            market_data[symbol] = data

        # Add macro context (simplified - in production would fetch from macro API)
        market_data["_macro"] = self._get_macro_context()

        return market_data

    def _get_macro_context(self) -> dict:
        """
        Get current macro context.

        In production, this would fetch from:
        - Fed API for policy stance
        - Economic indicators API
        - Bond market data
        """
        # Simplified macro context for MVP
        # In production, fetch this from real data sources
        return {
            "fed_stance": "neutral",
            "fed_stance_change": False,
            "inflation_trend": "falling",
            "yield_curve": "normal",
            "leading_indicators": "stable",
        }

    async def get_trigger_summary(
        self,
        triggered: List[TriggeredAsset],
    ) -> dict:
        """Generate a summary of detected triggers."""
        if not triggered:
            return {
                "total_triggers": 0,
                "by_type": {},
                "by_priority": {},
                "symbols": [],
            }

        by_type = {}
        by_priority = {"high": 0, "medium": 0, "low": 0}

        for t in triggered:
            trigger_type = t.trigger_type.value
            by_type[trigger_type] = by_type.get(trigger_type, 0) + 1
            by_priority[t.priority] = by_priority.get(t.priority, 0) + 1

        return {
            "total_triggers": len(triggered),
            "by_type": by_type,
            "by_priority": by_priority,
            "symbols": [t.symbol for t in triggered],
            "high_priority": [t.to_dict() for t in triggered if t.priority == "high"],
        }


# Default watchlist for scanning
DEFAULT_WATCHLIST = [
    # Mag 7
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    # Large Cap Value
    "BRK.B", "JPM", "JNJ", "PG", "KO", "XOM", "CVX",
    # Growth
    "PLTR", "SNOW", "CRWD", "NET", "DDOG",
    # Financials
    "GS", "MS", "BAC", "C",
    # Healthcare
    "UNH", "LLY", "PFE", "MRK",
    # Consumer
    "COST", "WMT", "HD", "NKE",
]
