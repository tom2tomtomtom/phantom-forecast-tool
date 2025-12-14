"""
Macro shift trigger detection (Dalio patterns).

Detects:
- Regime changes (Fed pivots, inflation trend reversals)
- Cycle turns (leading indicators bottoming/topping)
- Sector rotation opportunities
"""

from typing import List
from datetime import datetime

from .base import BaseTrigger, TriggeredAsset, TriggerType


class MacroShiftTrigger(BaseTrigger):
    """
    Detects macro regime changes and cycle shifts.

    These are patterns Dalio would recognize - understanding where
    we are in economic cycles and how policy shifts create opportunities.
    """

    name = "macro_shift"
    description = "Detects macro regime changes and cycle turns"

    async def detect(
        self,
        symbols: List[str],
        market_data: dict,
    ) -> List[TriggeredAsset]:
        """
        Detect macro-driven opportunities.

        For macro triggers, we analyze the broader market context
        and then identify which symbols benefit from the shift.

        Args:
            symbols: Ticker symbols to analyze
            market_data: Dict with macro context and sector data
                Expected structure: {
                    "_macro": {
                        "fed_stance": str,  # "hawkish", "neutral", "dovish"
                        "fed_stance_change": bool,
                        "inflation_trend": str,  # "rising", "stable", "falling"
                        "yield_curve": str,  # "inverted", "flat", "normal"
                        "leading_indicators": str,  # "declining", "bottoming", "rising"
                    },
                    "AAPL": {
                        "sector": str,
                        "beta": float,
                        "rate_sensitivity": str,  # "high", "medium", "low"
                    }
                }
        """
        triggered = []

        macro = market_data.get("_macro", {})
        if not macro:
            return triggered

        # Check for regime change
        regime_change = self._detect_regime_change(macro)

        # Check for cycle turn
        cycle_turn = self._detect_cycle_turn(macro)

        # If macro shift detected, find benefiting symbols
        if regime_change or cycle_turn:
            for symbol in symbols:
                data = market_data.get(symbol, {})
                if not data:
                    continue

                if regime_change:
                    trigger = self._check_regime_beneficiary(symbol, data, regime_change, macro)
                    if trigger:
                        triggered.append(trigger)
                        continue

                if cycle_turn:
                    trigger = self._check_cycle_beneficiary(symbol, data, cycle_turn, macro)
                    if trigger:
                        triggered.append(trigger)

        return triggered

    def _detect_regime_change(self, macro: dict) -> str | None:
        """Detect if a monetary policy regime change is occurring."""
        fed_stance = macro.get("fed_stance", "neutral")
        fed_change = macro.get("fed_stance_change", False)
        inflation_trend = macro.get("inflation_trend", "stable")

        # Fed pivot detection
        if fed_change:
            if fed_stance == "dovish":
                return "fed_pivot_dovish"
            elif fed_stance == "hawkish":
                return "fed_pivot_hawkish"

        # Inflation trend reversal
        if inflation_trend == "falling" and macro.get("inflation_was_rising"):
            return "inflation_peak"
        elif inflation_trend == "rising" and macro.get("inflation_was_falling"):
            return "inflation_trough"

        return None

    def _detect_cycle_turn(self, macro: dict) -> str | None:
        """Detect if an economic cycle turn is occurring."""
        leading_indicators = macro.get("leading_indicators", "stable")
        yield_curve = macro.get("yield_curve", "normal")

        # Cycle bottoming
        if leading_indicators == "bottoming":
            return "cycle_bottom"

        # Cycle topping
        if leading_indicators == "declining" and yield_curve == "inverted":
            return "cycle_top"

        return None

    def _check_regime_beneficiary(
        self,
        symbol: str,
        data: dict,
        regime_change: str,
        macro: dict,
    ) -> TriggeredAsset | None:
        """Check if symbol benefits from the regime change."""
        sector = data.get("sector", "")
        rate_sensitivity = data.get("rate_sensitivity", "medium")
        beta = data.get("beta", 1.0)

        # Fed dovish pivot benefits
        if regime_change == "fed_pivot_dovish":
            # Rate-sensitive sectors benefit
            if rate_sensitivity == "high" or sector in ["Technology", "Real Estate", "Consumer Discretionary"]:
                return TriggeredAsset(
                    symbol=symbol,
                    trigger_type=TriggerType.REGIME_CHANGE,
                    trigger_reason=f"Fed dovish pivot - {sector} sector benefits from lower rates",
                    priority="high",
                    relevant_phantoms=self.get_relevant_phantoms(TriggerType.REGIME_CHANGE),
                    detected_at=datetime.utcnow(),
                    metrics={
                        "regime_change": regime_change,
                        "sector": sector,
                        "rate_sensitivity": rate_sensitivity,
                        "fed_stance": macro.get("fed_stance"),
                    }
                )

        # Fed hawkish pivot - defensive plays
        if regime_change == "fed_pivot_hawkish":
            if sector in ["Utilities", "Consumer Staples", "Healthcare"] or (beta and beta < 0.8):
                return TriggeredAsset(
                    symbol=symbol,
                    trigger_type=TriggerType.REGIME_CHANGE,
                    trigger_reason=f"Fed hawkish pivot - defensive {sector} sector may outperform",
                    priority="medium",
                    relevant_phantoms=self.get_relevant_phantoms(TriggerType.REGIME_CHANGE),
                    detected_at=datetime.utcnow(),
                    metrics={
                        "regime_change": regime_change,
                        "sector": sector,
                        "beta": beta,
                        "fed_stance": macro.get("fed_stance"),
                    }
                )

        # Inflation peak - growth stocks benefit
        if regime_change == "inflation_peak":
            if sector in ["Technology", "Communication Services"] or (beta and beta > 1.2):
                return TriggeredAsset(
                    symbol=symbol,
                    trigger_type=TriggerType.REGIME_CHANGE,
                    trigger_reason=f"Inflation peaking - growth rotation favors {sector}",
                    priority="medium",
                    relevant_phantoms=self.get_relevant_phantoms(TriggerType.REGIME_CHANGE),
                    detected_at=datetime.utcnow(),
                    metrics={
                        "regime_change": regime_change,
                        "sector": sector,
                        "inflation_trend": macro.get("inflation_trend"),
                    }
                )

        return None

    def _check_cycle_beneficiary(
        self,
        symbol: str,
        data: dict,
        cycle_turn: str,
        macro: dict,
    ) -> TriggeredAsset | None:
        """Check if symbol benefits from cycle turn."""
        sector = data.get("sector", "")
        beta = data.get("beta", 1.0)

        # Cycle bottom - cyclicals lead the recovery
        if cycle_turn == "cycle_bottom":
            if sector in ["Industrials", "Materials", "Financials", "Consumer Discretionary"]:
                return TriggeredAsset(
                    symbol=symbol,
                    trigger_type=TriggerType.CYCLE_TURN,
                    trigger_reason=f"Economic cycle bottoming - cyclical {sector} positioned for recovery",
                    priority="high",
                    relevant_phantoms=self.get_relevant_phantoms(TriggerType.CYCLE_TURN),
                    detected_at=datetime.utcnow(),
                    metrics={
                        "cycle_turn": cycle_turn,
                        "sector": sector,
                        "leading_indicators": macro.get("leading_indicators"),
                    }
                )

        # Cycle top - rotate to defensives
        if cycle_turn == "cycle_top":
            if sector in ["Utilities", "Consumer Staples", "Healthcare"] or (beta and beta < 0.7):
                return TriggeredAsset(
                    symbol=symbol,
                    trigger_type=TriggerType.CYCLE_TURN,
                    trigger_reason=f"Economic cycle topping - defensive {sector} for protection",
                    priority="medium",
                    relevant_phantoms=self.get_relevant_phantoms(TriggerType.CYCLE_TURN),
                    detected_at=datetime.utcnow(),
                    metrics={
                        "cycle_turn": cycle_turn,
                        "sector": sector,
                        "yield_curve": macro.get("yield_curve"),
                    }
                )

        return None

    def get_relevant_phantoms(self, trigger_type: TriggerType) -> List[str]:
        """Return phantoms most relevant to macro triggers."""
        phantom_map = {
            TriggerType.REGIME_CHANGE: ["dalio", "burry", "buffett"],
            TriggerType.CYCLE_TURN: ["dalio", "buffett", "lynch"],
            TriggerType.SECTOR_ROTATION: ["dalio", "lynch"],
        }
        return phantom_map.get(trigger_type, ["dalio", "buffett"])
