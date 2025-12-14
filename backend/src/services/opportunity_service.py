"""
Opportunity storage service.

Handles saving, retrieving, and managing opportunity scan results.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.opportunity import Opportunity, OpportunityCreate


class OpportunityService:
    """Service for managing opportunity storage and retrieval."""

    def __init__(self, db: Session):
        self.db = db

    def save_opportunity(self, data: OpportunityCreate) -> Opportunity:
        """Save a single opportunity to the database."""
        opportunity = Opportunity(
            symbol=data.symbol.upper(),
            scan_id=data.scan_id,
            opportunity_score=data.opportunity_score,
            consensus_position=data.consensus_position,
            consensus_strength=data.consensus_strength,
            high_conviction_count=data.high_conviction_count,
            total_phantoms=data.total_phantoms,
            bullish_phantoms=data.bullish_phantoms,
            bearish_phantoms=data.bearish_phantoms,
            key_insight=data.key_insight,
            market_context=data.market_context,
            full_analysis=data.full_analysis,
            price_at_scan=data.price_at_scan,
        )

        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)

        return opportunity

    def save_batch(self, opportunities: List[OpportunityCreate], scan_id: Optional[str] = None) -> List[Opportunity]:
        """Save multiple opportunities from a single scan."""
        if not scan_id:
            scan_id = str(uuid.uuid4())

        saved = []
        for data in opportunities:
            data.scan_id = scan_id
            opportunity = Opportunity(
                symbol=data.symbol.upper(),
                scan_id=scan_id,
                opportunity_score=data.opportunity_score,
                consensus_position=data.consensus_position,
                consensus_strength=data.consensus_strength,
                high_conviction_count=data.high_conviction_count,
                total_phantoms=data.total_phantoms,
                bullish_phantoms=data.bullish_phantoms,
                bearish_phantoms=data.bearish_phantoms,
                key_insight=data.key_insight,
                market_context=data.market_context,
                full_analysis=data.full_analysis,
                price_at_scan=data.price_at_scan,
            )
            self.db.add(opportunity)
            saved.append(opportunity)

        self.db.commit()

        # Refresh all to get IDs
        for opp in saved:
            self.db.refresh(opp)

        return saved

    def get_by_id(self, opportunity_id: str) -> Optional[Opportunity]:
        """Get a single opportunity by ID."""
        return self.db.query(Opportunity).filter(
            Opportunity.id == opportunity_id
        ).first()

    def get_by_scan_id(self, scan_id: str) -> List[Opportunity]:
        """Get all opportunities from a specific scan."""
        return self.db.query(Opportunity).filter(
            Opportunity.scan_id == scan_id
        ).order_by(desc(Opportunity.opportunity_score)).all()

    def get_by_symbol(
        self,
        symbol: str,
        limit: int = 10,
        days: Optional[int] = None
    ) -> List[Opportunity]:
        """Get historical opportunities for a symbol."""
        query = self.db.query(Opportunity).filter(
            Opportunity.symbol == symbol.upper()
        )

        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Opportunity.scanned_at >= cutoff)

        return query.order_by(desc(Opportunity.scanned_at)).limit(limit).all()

    def get_recent(
        self,
        limit: int = 20,
        min_score: float = 0.0,
        days: int = 7
    ) -> List[Opportunity]:
        """Get recent opportunities above a minimum score."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        return self.db.query(Opportunity).filter(
            Opportunity.scanned_at >= cutoff,
            Opportunity.opportunity_score >= min_score
        ).order_by(
            desc(Opportunity.opportunity_score),
            desc(Opportunity.scanned_at)
        ).limit(limit).all()

    def get_top_opportunities(
        self,
        limit: int = 10,
        days: int = 7
    ) -> List[Opportunity]:
        """Get top scoring opportunities from recent scans."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        return self.db.query(Opportunity).filter(
            Opportunity.scanned_at >= cutoff
        ).order_by(
            desc(Opportunity.opportunity_score)
        ).limit(limit).all()

    def get_by_consensus(
        self,
        position: str,
        limit: int = 20,
        days: int = 7
    ) -> List[Opportunity]:
        """Get opportunities by consensus position."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        return self.db.query(Opportunity).filter(
            Opportunity.scanned_at >= cutoff,
            Opportunity.consensus_position == position
        ).order_by(
            desc(Opportunity.opportunity_score)
        ).limit(limit).all()

    def update_price(
        self,
        opportunity_id: str,
        current_price: float
    ) -> Optional[Opportunity]:
        """Update current price and calculate performance."""
        opportunity = self.get_by_id(opportunity_id)

        if not opportunity:
            return None

        opportunity.current_price = current_price
        opportunity.last_price_update = datetime.utcnow()

        if opportunity.price_at_scan and opportunity.price_at_scan > 0:
            opportunity.price_change_pct = (
                (current_price - opportunity.price_at_scan) / opportunity.price_at_scan * 100
            )

        self.db.commit()
        self.db.refresh(opportunity)

        return opportunity

    def delete_old(self, days: int = 90) -> int:
        """Delete opportunities older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        deleted = self.db.query(Opportunity).filter(
            Opportunity.scanned_at < cutoff
        ).delete()

        self.db.commit()

        return deleted

    def delete_by_id(self, opportunity_id: str) -> bool:
        """Delete a single opportunity by ID."""
        opportunity = self.get_by_id(opportunity_id)
        if not opportunity:
            return False

        self.db.delete(opportunity)
        self.db.commit()
        return True

    def delete_by_scan_id(self, scan_id: str) -> int:
        """Delete all opportunities from a specific scan."""
        deleted = self.db.query(Opportunity).filter(
            Opportunity.scan_id == scan_id
        ).delete()

        self.db.commit()
        return deleted

    def delete_all(self) -> int:
        """Delete all opportunities."""
        deleted = self.db.query(Opportunity).delete()
        self.db.commit()
        return deleted

    def get_stats(self, days: int = 30) -> dict:
        """Get opportunity statistics."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        opportunities = self.db.query(Opportunity).filter(
            Opportunity.scanned_at >= cutoff
        ).all()

        if not opportunities:
            return {
                "total_scans": 0,
                "unique_symbols": 0,
                "avg_score": 0,
                "high_score_count": 0,
                "bullish_count": 0,
                "bearish_count": 0,
            }

        scores = [o.opportunity_score for o in opportunities]
        symbols = set(o.symbol for o in opportunities)

        return {
            "total_scans": len(opportunities),
            "unique_symbols": len(symbols),
            "avg_score": sum(scores) / len(scores),
            "high_score_count": sum(1 for s in scores if s >= 7),
            "bullish_count": sum(1 for o in opportunities if o.consensus_position == "bullish"),
            "bearish_count": sum(1 for o in opportunities if o.consensus_position == "bearish"),
        }
