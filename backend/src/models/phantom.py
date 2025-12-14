"""
Pydantic models for Phantom data structures.

Based on patterns from congressional-trading-system schemas.py.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Position(str, Enum):
    """Investment position recommendation."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    AVOID = "avoid"


class Conviction(str, Enum):
    """Conviction level for a position."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Phantom Definition Models

class PhantomMemory(BaseModel):
    """A formative memory that shapes phantom judgment."""
    context: str = Field(..., description="Historical market situation")
    decision: str = Field(..., description="What the phantom did")
    reasoning: str = Field(..., description="Strategic logic behind the decision")
    outcome: str = Field(..., description="What happened as a result")
    lesson: str = Field(..., description="Strategic insight gained")


class PhantomDefinition(BaseModel):
    """Complete phantom persona definition."""
    investor_id: str = Field(..., description="Unique identifier (e.g., 'buffett')")
    name: str = Field(..., description="Full name (e.g., 'Warren Buffett')")
    era: str = Field(..., description="Investment era and context")
    philosophy: str = Field(..., description="Core investment philosophy")
    phantom_memories: List[PhantomMemory] = Field(default_factory=list)
    trigger_patterns: List[str] = Field(default_factory=list)
    blind_spots: List[str] = Field(default_factory=list)
    decision_framework: List[str] = Field(default_factory=list)


class PhantomSummary(BaseModel):
    """Brief phantom info for listing."""
    investor_id: str
    name: str
    philosophy: str


# Analysis Models

class AnalysisRequest(BaseModel):
    """Request for phantom analysis."""
    asset: str = Field(..., description="Asset to analyze (e.g., 'AAPL', 'BTC')")
    context: Optional[str] = Field(None, description="Additional market context")
    phantom_ids: Optional[List[str]] = Field(None, description="Specific phantoms to use (default: all)")


class PhantomAnalysis(BaseModel):
    """Analysis result from a single phantom."""
    phantom_id: str
    phantom_name: str
    position: Position
    conviction: Conviction
    reasoning: str = Field(..., description="Strategic reasoning for the position")
    key_factors: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    blind_spots_acknowledged: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CouncilAnalysis(BaseModel):
    """Combined analysis from all phantoms (the council)."""
    asset: str
    analyses: List[PhantomAnalysis]
    consensus: Optional[Position] = Field(None, description="Consensus position if any")
    disagreements: List[str] = Field(default_factory=list, description="Key points of disagreement")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Response Models

class PhantomListResponse(BaseModel):
    """Response for listing phantoms."""
    phantoms: List[PhantomSummary]
    total: int


class AnalysisResponse(BaseModel):
    """Response for a single phantom analysis."""
    success: bool
    analysis: Optional[PhantomAnalysis] = None
    error: Optional[str] = None


class CouncilResponse(BaseModel):
    """Response for council (all phantoms) analysis."""
    success: bool
    council: Optional[CouncilAnalysis] = None
    error: Optional[str] = None
