"""
Base trigger class and common types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime


class TriggerType(str, Enum):
    """Types of market triggers."""
    MASSIVE_DRAWDOWN = "massive_drawdown"
    VALUATION_DISLOCATION = "valuation_dislocation"
    SHORT_SQUEEZE_SETUP = "short_squeeze_setup"
    MOAT_EXPANSION = "moat_expansion"
    CRISIS_OPPORTUNITY = "crisis_opportunity"
    REGIME_CHANGE = "regime_change"
    CYCLE_TURN = "cycle_turn"
    EARNINGS_SURPRISE = "earnings_surprise"
    SECTOR_ROTATION = "sector_rotation"


@dataclass
class TriggeredAsset:
    """Asset that has triggered an opportunity signal."""
    symbol: str
    trigger_type: TriggerType
    trigger_reason: str
    priority: str  # high, medium, low
    relevant_phantoms: List[str]  # Which phantoms should analyze this
    detected_at: datetime
    metrics: dict  # Supporting data for the trigger

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "trigger_type": self.trigger_type.value,
            "trigger_reason": self.trigger_reason,
            "priority": self.priority,
            "relevant_phantoms": self.relevant_phantoms,
            "detected_at": self.detected_at.isoformat(),
            "metrics": self.metrics,
        }


class BaseTrigger(ABC):
    """
    Base class for trigger detectors.

    Each trigger type implements specific detection logic for
    market patterns that warrant phantom council analysis.
    """

    name: str = "base"
    description: str = "Base trigger"

    @abstractmethod
    async def detect(
        self,
        symbols: List[str],
        market_data: dict,
    ) -> List[TriggeredAsset]:
        """
        Detect trigger conditions for given symbols.

        Args:
            symbols: List of ticker symbols to check
            market_data: Pre-fetched market data for efficiency

        Returns:
            List of TriggeredAsset objects for symbols that triggered
        """
        pass

    @abstractmethod
    def get_relevant_phantoms(self, trigger_type: TriggerType) -> List[str]:
        """Return phantom IDs most relevant to this trigger type."""
        pass
