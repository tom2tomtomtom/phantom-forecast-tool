"""
Quality inflection trigger detection (Buffett/Munger patterns).

Detects:
- Moat expansion (market share gains + pricing power)
- Crisis opportunity (sector down but company moat intact)
- Margin expansion with revenue growth
"""

from typing import List, Optional
from datetime import datetime

from .base import BaseTrigger, TriggeredAsset, TriggerType


class QualityInflectionTrigger(BaseTrigger):
    """
    Detects quality inflection points - moments when durable
    competitive advantages are either strengthening or being
    offered at crisis prices.

    These are patterns Buffett and Munger would recognize.
    """

    name = "quality_inflection"
    description = "Detects quality companies at inflection points"

    # Configurable thresholds
    SECTOR_DRAWDOWN_THRESHOLD = -15.0  # Sector down 15%
    MARGIN_EXPANSION_THRESHOLD = 2.0  # 2 percentage points
    REVENUE_GROWTH_THRESHOLD = 10.0  # 10% YoY growth

    async def detect(
        self,
        symbols: List[str],
        market_data: dict,
    ) -> List[TriggeredAsset]:
        """
        Detect quality inflection points.

        Args:
            symbols: Ticker symbols to analyze
            market_data: Dict with quote and financial data per symbol
                Expected structure: {
                    "AAPL": {
                        "quote": StockQuote,
                        "financials": BasicFinancials,
                        "sector": str,
                        "sector_performance_30d": float,
                        "gross_margin": float,
                        "gross_margin_yoy_change": float,
                        "revenue_growth_yoy": float,
                        "market_share_trend": str  # "increasing", "stable", "decreasing"
                    }
                }
        """
        triggered = []

        for symbol in symbols:
            data = market_data.get(symbol, {})
            if not data:
                continue

            # Check for crisis opportunity
            crisis_trigger = self._check_crisis_opportunity(symbol, data)
            if crisis_trigger:
                triggered.append(crisis_trigger)
                continue

            # Check for moat expansion
            moat_trigger = self._check_moat_expansion(symbol, data)
            if moat_trigger:
                triggered.append(moat_trigger)

        return triggered

    def _check_crisis_opportunity(
        self,
        symbol: str,
        data: dict,
    ) -> Optional[TriggeredAsset]:
        """
        Check for sector crisis with company moat intact.

        Classic Buffett: "Be greedy when others are fearful"
        """
        sector_perf = data.get("sector_performance_30d", 0)
        financials = data.get("financials")
        quote = data.get("quote")

        # Sector must be significantly down
        if sector_perf > self.SECTOR_DRAWDOWN_THRESHOLD:
            return None

        # Company must show quality characteristics
        quality_score = 0
        quality_reasons = []

        if financials:
            # Check PE is reasonable (not distressed)
            pe = financials.pe_ratio if hasattr(financials, 'pe_ratio') else data.get("pe_ratio")
            if pe and 5 < pe < 30:
                quality_score += 1
                quality_reasons.append(f"Reasonable PE ({pe:.1f})")

            # Check ROE is strong
            roe = financials.roe if hasattr(financials, 'roe') else data.get("roe")
            if roe and roe > 15:
                quality_score += 1
                quality_reasons.append(f"Strong ROE ({roe:.1f}%)")

            # Check dividend (stability indicator)
            div_yield = financials.dividend_yield if hasattr(financials, 'dividend_yield') else data.get("dividend_yield")
            if div_yield and div_yield > 0:
                quality_score += 1
                quality_reasons.append(f"Pays dividend ({div_yield:.2f}%)")

        # Check price vs 52-week range (is it beaten down?)
        if quote and financials:
            week_52_high = financials.week_52_high if hasattr(financials, 'week_52_high') else data.get("week_52_high")
            current_price = quote.current_price if hasattr(quote, 'current_price') else data.get("current_price")

            if week_52_high and current_price:
                pct_from_high = ((current_price - week_52_high) / week_52_high) * 100
                if pct_from_high < -20:
                    quality_score += 1
                    quality_reasons.append(f"{abs(pct_from_high):.1f}% off 52-week high")

        # Need at least 2 quality indicators
        if quality_score >= 2:
            return TriggeredAsset(
                symbol=symbol,
                trigger_type=TriggerType.CRISIS_OPPORTUNITY,
                trigger_reason=f"Sector down {abs(sector_perf):.1f}% but quality intact: {', '.join(quality_reasons)}",
                priority="high",
                relevant_phantoms=self.get_relevant_phantoms(TriggerType.CRISIS_OPPORTUNITY),
                detected_at=datetime.utcnow(),
                metrics={
                    "sector_performance_30d": sector_perf,
                    "quality_score": quality_score,
                    "quality_reasons": quality_reasons,
                }
            )

        return None

    def _check_moat_expansion(
        self,
        symbol: str,
        data: dict,
    ) -> Optional[TriggeredAsset]:
        """
        Check for signs of strengthening competitive advantage.

        Indicators: margin expansion + revenue growth + market share gains
        """
        margin_change = data.get("gross_margin_yoy_change", 0)
        revenue_growth = data.get("revenue_growth_yoy", 0)
        market_share_trend = data.get("market_share_trend", "stable")

        signals = []

        # Margin expansion
        if margin_change >= self.MARGIN_EXPANSION_THRESHOLD:
            signals.append(f"Margin expanding ({margin_change:+.1f} pts)")

        # Revenue growth
        if revenue_growth >= self.REVENUE_GROWTH_THRESHOLD:
            signals.append(f"Revenue growing ({revenue_growth:.1f}% YoY)")

        # Market share gains
        if market_share_trend == "increasing":
            signals.append("Market share increasing")

        # Need at least 2 signals for moat expansion
        if len(signals) >= 2:
            return TriggeredAsset(
                symbol=symbol,
                trigger_type=TriggerType.MOAT_EXPANSION,
                trigger_reason=f"Moat strengthening: {', '.join(signals)}",
                priority="medium",
                relevant_phantoms=self.get_relevant_phantoms(TriggerType.MOAT_EXPANSION),
                detected_at=datetime.utcnow(),
                metrics={
                    "gross_margin_yoy_change": margin_change,
                    "revenue_growth_yoy": revenue_growth,
                    "market_share_trend": market_share_trend,
                    "signals": signals,
                }
            )

        return None

    def get_relevant_phantoms(self, trigger_type: TriggerType) -> List[str]:
        """Return phantoms most relevant to quality triggers."""
        phantom_map = {
            TriggerType.CRISIS_OPPORTUNITY: ["buffett", "munger", "ackman"],
            TriggerType.MOAT_EXPANSION: ["buffett", "munger", "lynch"],
        }
        return phantom_map.get(trigger_type, ["buffett", "munger"])
