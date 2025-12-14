"""
Opportunity model for storing scan results.

Tracks phantom council analysis results for historical tracking and performance measurement.
"""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON

from ..services.database import Base


class Opportunity(Base):
    """SQLAlchemy model for opportunities table."""

    __tablename__ = "opportunities"

    # Use String for UUID to work with both SQLite and PostgreSQL
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Asset info
    symbol = Column(String(10), nullable=False, index=True)

    # Scan metadata
    scan_id = Column(String(36), index=True)
    scanned_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Scoring
    opportunity_score = Column(Float, nullable=False)

    # Council analysis summary
    consensus_position = Column(String(20))  # bullish, bearish, neutral, null
    consensus_strength = Column(String(20))  # strong, weak, none
    high_conviction_count = Column(Integer, default=0)
    total_phantoms = Column(Integer, default=6)

    # Phantom positions (stored as JSON for SQLite compatibility)
    bullish_phantoms = Column(JSON, default=list)
    bearish_phantoms = Column(JSON, default=list)

    # Insights
    key_insight = Column(Text, nullable=False)
    market_context = Column(Text)

    # Full analysis (JSON for flexibility)
    full_analysis = Column(JSON)

    # Market data at scan time
    price_at_scan = Column(Float)

    # Performance tracking (updated later)
    current_price = Column(Float)
    price_change_pct = Column(Float)
    last_price_update = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Opportunity {self.symbol} score={self.opportunity_score}>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "symbol": self.symbol,
            "scan_id": str(self.scan_id) if self.scan_id else None,
            "scanned_at": self.scanned_at.isoformat() if self.scanned_at else None,
            "opportunity_score": self.opportunity_score,
            "consensus_position": self.consensus_position,
            "consensus_strength": self.consensus_strength,
            "high_conviction_count": self.high_conviction_count,
            "total_phantoms": self.total_phantoms,
            "bullish_phantoms": self.bullish_phantoms or [],
            "bearish_phantoms": self.bearish_phantoms or [],
            "key_insight": self.key_insight,
            "market_context": self.market_context,
            "price_at_scan": self.price_at_scan,
            "current_price": self.current_price,
            "price_change_pct": self.price_change_pct,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Pydantic models for API
from pydantic import BaseModel


class OpportunityCreate(BaseModel):
    """Schema for creating an opportunity."""
    symbol: str
    scan_id: Optional[str] = None
    opportunity_score: float
    consensus_position: Optional[str] = None
    consensus_strength: Optional[str] = None
    high_conviction_count: int = 0
    total_phantoms: int = 6
    bullish_phantoms: List[str] = []
    bearish_phantoms: List[str] = []
    key_insight: str
    market_context: Optional[str] = None
    full_analysis: Optional[dict] = None
    price_at_scan: Optional[float] = None


class OpportunityResponse(BaseModel):
    """Schema for opportunity API response."""
    id: str
    symbol: str
    scan_id: Optional[str]
    scanned_at: Optional[str]
    opportunity_score: float
    consensus_position: Optional[str]
    consensus_strength: Optional[str]
    high_conviction_count: int
    total_phantoms: int
    bullish_phantoms: List[str]
    bearish_phantoms: List[str]
    key_insight: str
    market_context: Optional[str]
    price_at_scan: Optional[float]
    current_price: Optional[float]
    price_change_pct: Optional[float]
    created_at: Optional[str]

    class Config:
        from_attributes = True
