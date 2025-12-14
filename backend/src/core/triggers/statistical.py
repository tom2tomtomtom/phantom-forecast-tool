"""
Statistical anomaly trigger detection (Burry patterns).

Detects:
- Massive drawdowns with stable fundamentals
- Valuation dislocations (PE < 50% of 5yr avg)
- Short squeeze setups (high short interest + quality)
"""

from typing import List
from datetime import datetime

from .base import BaseTrigger, TriggeredAsset, TriggerType


class StatisticalAnomalyTrigger(BaseTrigger):
    """
    Detects statistical anomalies that may indicate mispricing.

    These are patterns Burry would recognize - quantitative dislocations
    from historical norms that suggest market inefficiency.
    """

    name = "statistical_anomaly"
    description = "Detects statistical dislocations and anomalies"

    # Configurable thresholds
    DRAWDOWN_THRESHOLD = -20.0  # 20% drop
    PE_DISLOCATION_RATIO = 0.5  # Current PE < 50% of 5yr avg
    SHORT_INTEREST_THRESHOLD = 20.0  # 20% short interest

    async def detect(
        self,
        symbols: List[str],
        market_data: dict,
    ) -> List[TriggeredAsset]:
        """
        Detect statistical anomalies in the given symbols.

        Args:
            symbols: Ticker symbols to analyze
            market_data: Dict with quote and financial data per symbol
                Expected structure: {
                    "AAPL": {
                        "quote": StockQuote,
                        "financials": BasicFinancials,
                        "price_change_30d": float,
                        "avg_pe_5yr": float,
                        "short_interest": float
                    }
                }
        """
        triggered = []

        for symbol in symbols:
            data = market_data.get(symbol, {})
            if not data:
                continue

            # Check for massive drawdown
            drawdown_trigger = self._check_massive_drawdown(symbol, data)
            if drawdown_trigger:
                triggered.append(drawdown_trigger)
                continue  # One trigger per symbol

            # Check for valuation dislocation
            valuation_trigger = self._check_valuation_dislocation(symbol, data)
            if valuation_trigger:
                triggered.append(valuation_trigger)
                continue

            # Check for short squeeze setup
            squeeze_trigger = self._check_short_squeeze(symbol, data)
            if squeeze_trigger:
                triggered.append(squeeze_trigger)

        return triggered

    def _check_massive_drawdown(
        self,
        symbol: str,
        data: dict,
    ) -> TriggeredAsset | None:
        """Check for massive price drop with stable fundamentals."""
        price_change = data.get("price_change_30d", 0)
        financials = data.get("financials")

        if price_change > self.DRAWDOWN_THRESHOLD:
            return None

        # Check if fundamentals are still reasonable
        if financials:
            pe = financials.pe_ratio if hasattr(financials, 'pe_ratio') else data.get("pe_ratio")
            roe = financials.roe if hasattr(financials, 'roe') else data.get("roe")

            # Fundamentals check - positive PE and decent ROE
            fundamentals_stable = (pe and pe > 0 and pe < 50) or (roe and roe > 5)

            if fundamentals_stable:
                return TriggeredAsset(
                    symbol=symbol,
                    trigger_type=TriggerType.MASSIVE_DRAWDOWN,
                    trigger_reason=f"Down {abs(price_change):.1f}% in 30 days with stable fundamentals",
                    priority="high",
                    relevant_phantoms=self.get_relevant_phantoms(TriggerType.MASSIVE_DRAWDOWN),
                    detected_at=datetime.utcnow(),
                    metrics={
                        "price_change_30d": price_change,
                        "pe_ratio": pe,
                        "roe": roe,
                    }
                )

        return None

    def _check_valuation_dislocation(
        self,
        symbol: str,
        data: dict,
    ) -> TriggeredAsset | None:
        """Check if current PE is far below historical average."""
        financials = data.get("financials")
        avg_pe_5yr = data.get("avg_pe_5yr")

        if not financials or not avg_pe_5yr:
            return None

        current_pe = financials.pe_ratio if hasattr(financials, 'pe_ratio') else data.get("pe_ratio")

        if not current_pe or current_pe <= 0 or avg_pe_5yr <= 0:
            return None

        ratio = current_pe / avg_pe_5yr

        if ratio < self.PE_DISLOCATION_RATIO:
            return TriggeredAsset(
                symbol=symbol,
                trigger_type=TriggerType.VALUATION_DISLOCATION,
                trigger_reason=f"PE ratio {current_pe:.1f} is {ratio*100:.0f}% of 5yr avg ({avg_pe_5yr:.1f})",
                priority="high",
                relevant_phantoms=self.get_relevant_phantoms(TriggerType.VALUATION_DISLOCATION),
                detected_at=datetime.utcnow(),
                metrics={
                    "current_pe": current_pe,
                    "avg_pe_5yr": avg_pe_5yr,
                    "pe_ratio_vs_avg": ratio,
                }
            )

        return None

    def _check_short_squeeze(
        self,
        symbol: str,
        data: dict,
    ) -> TriggeredAsset | None:
        """Check for high short interest with quality fundamentals."""
        short_interest = data.get("short_interest", 0)
        financials = data.get("financials")

        if short_interest < self.SHORT_INTEREST_THRESHOLD:
            return None

        # Need some quality indicators
        if financials:
            roe = financials.roe if hasattr(financials, 'roe') else data.get("roe")
            if roe and roe > 10:  # Decent quality
                return TriggeredAsset(
                    symbol=symbol,
                    trigger_type=TriggerType.SHORT_SQUEEZE_SETUP,
                    trigger_reason=f"Short interest {short_interest:.1f}% with quality fundamentals (ROE: {roe:.1f}%)",
                    priority="medium",
                    relevant_phantoms=self.get_relevant_phantoms(TriggerType.SHORT_SQUEEZE_SETUP),
                    detected_at=datetime.utcnow(),
                    metrics={
                        "short_interest": short_interest,
                        "roe": roe,
                    }
                )

        return None

    def get_relevant_phantoms(self, trigger_type: TriggerType) -> List[str]:
        """Return phantoms most relevant to statistical triggers."""
        phantom_map = {
            TriggerType.MASSIVE_DRAWDOWN: ["burry", "buffett", "ackman"],
            TriggerType.VALUATION_DISLOCATION: ["burry", "buffett", "munger"],
            TriggerType.SHORT_SQUEEZE_SETUP: ["burry", "ackman"],
        }
        return phantom_map.get(trigger_type, ["burry", "buffett"])
