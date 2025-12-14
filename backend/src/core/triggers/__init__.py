"""
Trigger detection system for identifying market opportunities.

Each trigger type detects specific patterns that warrant phantom analysis.
"""

from .base import BaseTrigger, TriggeredAsset, TriggerType
from .statistical import StatisticalAnomalyTrigger
from .quality import QualityInflectionTrigger
from .macro import MacroShiftTrigger

__all__ = [
    "BaseTrigger",
    "TriggeredAsset",
    "TriggerType",
    "StatisticalAnomalyTrigger",
    "QualityInflectionTrigger",
    "MacroShiftTrigger",
]
