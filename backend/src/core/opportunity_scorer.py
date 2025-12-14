"""
Enhanced opportunity scoring algorithm.

Scores opportunities based on sophisticated council analysis patterns:
- High-conviction consensus
- Strategic disagreement (value vs growth tension)
- Blind spot arbitrage
- Contrarian quality
- Catalyst alignment
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

from ..models.phantom import PhantomAnalysis, Position, Conviction


class ScoringPattern(str, Enum):
    """Detected scoring patterns."""
    HIGH_CONVICTION_CONSENSUS = "high_conviction_consensus"
    STRATEGIC_DISAGREEMENT = "strategic_disagreement"
    BLIND_SPOT_ARBITRAGE = "blind_spot_arbitrage"
    CONTRARIAN_QUALITY = "contrarian_quality"
    CATALYST_ALIGNMENT = "catalyst_alignment"
    WEAK_CONSENSUS = "weak_consensus"
    UNANIMOUS_AVOID = "unanimous_avoid"


@dataclass
class PatternResult:
    """Result of pattern detection."""
    pattern: ScoringPattern
    detected: bool
    score_impact: float
    insight: str
    details: dict


@dataclass
class OpportunityScore:
    """Complete opportunity score with explanation."""
    score: float
    patterns_detected: List[PatternResult]
    primary_pattern: Optional[ScoringPattern]
    explanation: str
    action_items: List[str]
    risk_factors: List[str]
    phantom_breakdown: dict


class OpportunityScorer:
    """
    Scores opportunities based on council analysis patterns.

    Score ranges:
    - 9-10: Exceptional - rare high-conviction consensus or perfect disagreement
    - 7-8: Strong - clear opportunity signal from pattern
    - 5-6: Moderate - interesting but needs more research
    - 3-4: Weak - conflicting signals or low conviction
    - 1-2: Pass - consensus uncertainty or negative
    """

    def score(
        self,
        analyses: List[PhantomAnalysis],
        synthesis: dict,
        trigger_type: Optional[str] = None,
        market_sentiment: str = "neutral",
    ) -> OpportunityScore:
        """
        Calculate opportunity score from council patterns.

        Args:
            analyses: List of phantom analyses
            synthesis: Synthesis result from council
            trigger_type: What triggered this opportunity
            market_sentiment: Overall market sentiment
        """
        if not analyses:
            return self._empty_score()

        # Detect all patterns
        patterns = []

        # Pattern 1: High-conviction consensus
        consensus_pattern = self._check_high_conviction_consensus(analyses, synthesis)
        patterns.append(consensus_pattern)

        # Pattern 2: Strategic disagreement
        disagreement_pattern = self._check_strategic_disagreement(analyses)
        patterns.append(disagreement_pattern)

        # Pattern 3: Blind spot arbitrage
        blind_spot_pattern = self._check_blind_spot_arbitrage(analyses)
        patterns.append(blind_spot_pattern)

        # Pattern 4: Contrarian quality
        contrarian_pattern = self._check_contrarian_quality(analyses, market_sentiment)
        patterns.append(contrarian_pattern)

        # Pattern 5: Catalyst alignment
        if trigger_type:
            catalyst_pattern = self._check_catalyst_alignment(analyses, trigger_type)
            patterns.append(catalyst_pattern)

        # Pattern 6: Weak consensus (negative pattern)
        weak_pattern = self._check_weak_consensus(analyses)
        patterns.append(weak_pattern)

        # Calculate final score
        detected_patterns = [p for p in patterns if p.detected]

        if not detected_patterns:
            base_score = 4.0  # Default neutral
        else:
            # Take highest positive pattern score, subtract negative patterns
            positive_patterns = [p for p in detected_patterns if p.score_impact > 0]
            negative_patterns = [p for p in detected_patterns if p.score_impact < 0]

            if positive_patterns:
                base_score = max(p.score_impact for p in positive_patterns)
                # Bonus for multiple positive patterns
                if len(positive_patterns) > 1:
                    base_score += 0.5

            else:
                base_score = 4.0

            # Apply negative pattern penalties
            for neg in negative_patterns:
                base_score += neg.score_impact  # Negative values

        # Clamp to valid range
        final_score = max(1.0, min(10.0, base_score))

        # Determine primary pattern
        primary_pattern = None
        if detected_patterns:
            primary_pattern = max(detected_patterns, key=lambda p: abs(p.score_impact)).pattern

        # Generate explanation
        explanation = self._generate_explanation(detected_patterns, analyses)

        # Generate action items
        action_items = self._generate_action_items(detected_patterns, primary_pattern)

        # Extract risk factors
        risk_factors = self._extract_risk_factors(analyses)

        # Phantom breakdown
        phantom_breakdown = self._get_phantom_breakdown(analyses)

        return OpportunityScore(
            score=round(final_score, 1),
            patterns_detected=detected_patterns,
            primary_pattern=primary_pattern,
            explanation=explanation,
            action_items=action_items,
            risk_factors=risk_factors,
            phantom_breakdown=phantom_breakdown,
        )

    def _check_high_conviction_consensus(
        self,
        analyses: List[PhantomAnalysis],
        synthesis: dict,
    ) -> PatternResult:
        """
        Check for high-conviction agreement across diverse philosophies.

        This is rare - when Buffett, Burry, and Dalio all agree with high
        conviction, it's a strong signal.
        """
        high_conviction = [a for a in analyses if a.conviction == Conviction.HIGH]
        total = len(analyses)

        # Need at least 4 high conviction
        if len(high_conviction) < 4:
            return PatternResult(
                pattern=ScoringPattern.HIGH_CONVICTION_CONSENSUS,
                detected=False,
                score_impact=0,
                insight="",
                details={"high_conviction_count": len(high_conviction)},
            )

        # Check if they're pointing same direction
        bullish_hc = [a for a in high_conviction if a.position == Position.BULLISH]
        bearish_hc = [a for a in high_conviction if a.position in [Position.BEARISH, Position.AVOID]]

        if len(bullish_hc) >= 4:
            return PatternResult(
                pattern=ScoringPattern.HIGH_CONVICTION_CONSENSUS,
                detected=True,
                score_impact=9.5 if len(bullish_hc) >= 5 else 9.0,
                insight=f"Rare bullish consensus: {len(bullish_hc)} of {total} phantoms agree with high conviction",
                details={
                    "high_conviction_count": len(high_conviction),
                    "bullish_high_conviction": len(bullish_hc),
                    "direction": "bullish",
                },
            )

        if len(bearish_hc) >= 4:
            return PatternResult(
                pattern=ScoringPattern.HIGH_CONVICTION_CONSENSUS,
                detected=True,
                score_impact=2.0,  # Strong sell signal
                insight=f"Strong bearish consensus: {len(bearish_hc)} phantoms say avoid with high conviction",
                details={
                    "high_conviction_count": len(high_conviction),
                    "bearish_high_conviction": len(bearish_hc),
                    "direction": "bearish",
                },
            )

        return PatternResult(
            pattern=ScoringPattern.HIGH_CONVICTION_CONSENSUS,
            detected=False,
            score_impact=0,
            insight="",
            details={"high_conviction_count": len(high_conviction)},
        )

    def _check_strategic_disagreement(
        self,
        analyses: List[PhantomAnalysis],
    ) -> PatternResult:
        """
        Check for strategic disagreement between different investment styles.

        Key patterns:
        - Buffett avoid + Burry buy = value/growth tension (interesting!)
        - Quality phantoms vs quant phantoms disagreement
        """
        by_id = {a.phantom_id: a for a in analyses}

        buffett = by_id.get("buffett")
        burry = by_id.get("burry")
        munger = by_id.get("munger")
        dalio = by_id.get("dalio")
        ackman = by_id.get("ackman")
        lynch = by_id.get("lynch")

        # Pattern: Buffett/Munger cautious + Burry bullish = value dislocation
        if buffett and burry:
            buffett_cautious = buffett.position in [Position.NEUTRAL, Position.BEARISH, Position.AVOID]
            burry_bullish = burry.position == Position.BULLISH and burry.conviction == Conviction.HIGH

            if buffett_cautious and burry_bullish:
                return PatternResult(
                    pattern=ScoringPattern.STRATEGIC_DISAGREEMENT,
                    detected=True,
                    score_impact=8.0,
                    insight="Value vs Growth tension: Buffett cautious on moat durability but Burry sees statistical mispricing. Market uncertainty creating potential entry.",
                    details={
                        "buffett_position": buffett.position.value,
                        "burry_position": burry.position.value,
                        "burry_conviction": burry.conviction.value,
                        "disagreement_type": "value_growth_tension",
                    },
                )

        # Pattern: Quality phantoms vs activist
        if buffett and ackman:
            buffett_cautious = buffett.position in [Position.NEUTRAL, Position.BEARISH]
            ackman_bullish = ackman.position == Position.BULLISH and ackman.conviction in [Conviction.HIGH, Conviction.MEDIUM]

            if buffett_cautious and ackman_bullish:
                return PatternResult(
                    pattern=ScoringPattern.STRATEGIC_DISAGREEMENT,
                    detected=True,
                    score_impact=7.5,
                    insight="Activist opportunity: Buffett sees management/moat issues but Ackman sees activist value creation potential.",
                    details={
                        "buffett_position": buffett.position.value,
                        "ackman_position": ackman.position.value,
                        "disagreement_type": "quality_vs_activist",
                    },
                )

        # Pattern: Macro vs micro disagreement
        if dalio and lynch:
            dalio_cautious = dalio.position in [Position.BEARISH, Position.AVOID]
            lynch_bullish = lynch.position == Position.BULLISH

            if dalio_cautious and lynch_bullish:
                return PatternResult(
                    pattern=ScoringPattern.STRATEGIC_DISAGREEMENT,
                    detected=True,
                    score_impact=7.0,
                    insight="Macro vs Micro: Dalio concerned about macro headwinds but Lynch sees strong consumer fundamentals. Bottom-up vs top-down tension.",
                    details={
                        "dalio_position": dalio.position.value,
                        "lynch_position": lynch.position.value,
                        "disagreement_type": "macro_vs_micro",
                    },
                )

        return PatternResult(
            pattern=ScoringPattern.STRATEGIC_DISAGREEMENT,
            detected=False,
            score_impact=0,
            insight="",
            details={},
        )

    def _check_blind_spot_arbitrage(
        self,
        analyses: List[PhantomAnalysis],
    ) -> PatternResult:
        """
        Check if one phantom's strength covers another's blind spot.

        When a phantom acknowledges their blind spot but another phantom
        specifically addresses it - that's valuable synthesis.
        """
        acknowledged_blind_spots = []
        addressed_factors = []

        for a in analyses:
            if a.blind_spots_acknowledged:
                acknowledged_blind_spots.extend(a.blind_spots_acknowledged)
            if a.key_factors:
                addressed_factors.extend(a.key_factors)

        # Check for overlaps (simplified - in production use NLP similarity)
        overlap_keywords = ["valuation", "growth", "macro", "consumer", "moat", "management"]

        for blind_spot in acknowledged_blind_spots:
            blind_spot_lower = blind_spot.lower()
            for factor in addressed_factors:
                factor_lower = factor.lower()
                for keyword in overlap_keywords:
                    if keyword in blind_spot_lower and keyword in factor_lower:
                        return PatternResult(
                            pattern=ScoringPattern.BLIND_SPOT_ARBITRAGE,
                            detected=True,
                            score_impact=7.0,
                            insight=f"Blind spot coverage: One phantom's acknowledged weakness ({blind_spot[:50]}...) is addressed by another's strength.",
                            details={
                                "blind_spot": blind_spot,
                                "addressed_by": factor,
                                "keyword": keyword,
                            },
                        )

        return PatternResult(
            pattern=ScoringPattern.BLIND_SPOT_ARBITRAGE,
            detected=False,
            score_impact=0,
            insight="",
            details={},
        )

    def _check_contrarian_quality(
        self,
        analyses: List[PhantomAnalysis],
        market_sentiment: str,
    ) -> PatternResult:
        """
        Check for quality phantoms being positive when market is negative.

        Classic Buffett: "Be greedy when others are fearful"
        """
        if market_sentiment != "bearish":
            return PatternResult(
                pattern=ScoringPattern.CONTRARIAN_QUALITY,
                detected=False,
                score_impact=0,
                insight="",
                details={"market_sentiment": market_sentiment},
            )

        by_id = {a.phantom_id: a for a in analyses}

        quality_phantoms = ["buffett", "munger"]
        quality_bullish = []

        for pid in quality_phantoms:
            phantom = by_id.get(pid)
            if phantom and phantom.position in [Position.BULLISH, Position.NEUTRAL]:
                quality_bullish.append(phantom)

        if len(quality_bullish) >= 1:
            return PatternResult(
                pattern=ScoringPattern.CONTRARIAN_QUALITY,
                detected=True,
                score_impact=8.5,
                insight=f"Contrarian quality signal: Market bearish but quality-focused phantoms ({', '.join(p.phantom_name for p in quality_bullish)}) see value. Classic crisis opportunity pattern.",
                details={
                    "market_sentiment": market_sentiment,
                    "quality_bullish": [p.phantom_id for p in quality_bullish],
                },
            )

        return PatternResult(
            pattern=ScoringPattern.CONTRARIAN_QUALITY,
            detected=False,
            score_impact=0,
            insight="",
            details={"market_sentiment": market_sentiment},
        )

    def _check_catalyst_alignment(
        self,
        analyses: List[PhantomAnalysis],
        trigger_type: str,
    ) -> PatternResult:
        """
        Check if the trigger type aligns with phantom recommendations.

        E.g., if trigger is "massive_drawdown" and Burry is bullish,
        that's strong alignment.
        """
        trigger_phantom_alignment = {
            "massive_drawdown": ["burry", "buffett"],
            "valuation_dislocation": ["burry", "munger"],
            "crisis_opportunity": ["buffett", "ackman"],
            "moat_expansion": ["buffett", "munger"],
            "regime_change": ["dalio", "burry"],
            "cycle_turn": ["dalio", "lynch"],
        }

        relevant_phantoms = trigger_phantom_alignment.get(trigger_type, [])
        if not relevant_phantoms:
            return PatternResult(
                pattern=ScoringPattern.CATALYST_ALIGNMENT,
                detected=False,
                score_impact=0,
                insight="",
                details={"trigger_type": trigger_type},
            )

        by_id = {a.phantom_id: a for a in analyses}
        aligned = []

        for pid in relevant_phantoms:
            phantom = by_id.get(pid)
            if phantom and phantom.position == Position.BULLISH and phantom.conviction in [Conviction.HIGH, Conviction.MEDIUM]:
                aligned.append(phantom)

        if len(aligned) >= 1:
            return PatternResult(
                pattern=ScoringPattern.CATALYST_ALIGNMENT,
                detected=True,
                score_impact=7.5,
                insight=f"Catalyst alignment: Trigger '{trigger_type}' matches {', '.join(p.phantom_name for p in aligned)}'s strengths. They're bullish on this type of opportunity.",
                details={
                    "trigger_type": trigger_type,
                    "aligned_phantoms": [p.phantom_id for p in aligned],
                },
            )

        return PatternResult(
            pattern=ScoringPattern.CATALYST_ALIGNMENT,
            detected=False,
            score_impact=0,
            insight="",
            details={"trigger_type": trigger_type},
        )

    def _check_weak_consensus(
        self,
        analyses: List[PhantomAnalysis],
    ) -> PatternResult:
        """
        Check for weak or uncertain consensus (negative pattern).
        """
        low_conviction = [a for a in analyses if a.conviction == Conviction.LOW]
        neutral = [a for a in analyses if a.position == Position.NEUTRAL]

        # Too much uncertainty
        if len(low_conviction) >= 4 or len(neutral) >= 4:
            return PatternResult(
                pattern=ScoringPattern.WEAK_CONSENSUS,
                detected=True,
                score_impact=-2.0,  # Penalty
                insight=f"Weak conviction: {len(low_conviction)} low conviction, {len(neutral)} neutral positions. Council lacks clarity.",
                details={
                    "low_conviction_count": len(low_conviction),
                    "neutral_count": len(neutral),
                },
            )

        return PatternResult(
            pattern=ScoringPattern.WEAK_CONSENSUS,
            detected=False,
            score_impact=0,
            insight="",
            details={},
        )

    def _generate_explanation(
        self,
        detected_patterns: List[PatternResult],
        analyses: List[PhantomAnalysis],
    ) -> str:
        """Generate human-readable explanation of the score."""
        if not detected_patterns:
            return "Mixed signals across the council. No clear pattern detected."

        # Primary insight from highest-impact pattern
        primary = max(detected_patterns, key=lambda p: abs(p.score_impact))
        explanation = primary.insight

        # Add secondary patterns
        secondary = [p for p in detected_patterns if p != primary and p.detected]
        if secondary:
            explanation += f" Additionally: {secondary[0].insight}"

        return explanation

    def _generate_action_items(
        self,
        detected_patterns: List[PatternResult],
        primary_pattern: Optional[ScoringPattern],
    ) -> List[str]:
        """Generate actionable recommendations."""
        actions = []

        if primary_pattern == ScoringPattern.HIGH_CONVICTION_CONSENSUS:
            actions.append("Review position sizing - rare high-conviction consensus")
            actions.append("Check for any recent news that might invalidate thesis")

        elif primary_pattern == ScoringPattern.STRATEGIC_DISAGREEMENT:
            actions.append("Dig deeper into the source of disagreement")
            actions.append("Consider which phantom's view aligns with your own style")
            actions.append("This tension often resolves profitably - monitor closely")

        elif primary_pattern == ScoringPattern.CONTRARIAN_QUALITY:
            actions.append("Verify moat is truly intact despite market fear")
            actions.append("Consider dollar-cost averaging into position")
            actions.append("Set price alerts for further weakness")

        elif primary_pattern == ScoringPattern.CATALYST_ALIGNMENT:
            actions.append("Monitor the catalyst closely")
            actions.append("Set specific entry and exit criteria")

        elif primary_pattern == ScoringPattern.WEAK_CONSENSUS:
            actions.append("Wait for more clarity before acting")
            actions.append("This is not a high-conviction opportunity")

        if not actions:
            actions.append("Continue monitoring - no clear action at this time")

        return actions

    def _extract_risk_factors(
        self,
        analyses: List[PhantomAnalysis],
    ) -> List[str]:
        """Extract unique risk factors from all analyses."""
        all_risks = []
        for a in analyses:
            if a.risks:
                all_risks.extend(a.risks)

        # Deduplicate (simplified)
        unique_risks = list(set(all_risks))
        return unique_risks[:5]  # Top 5

    def _get_phantom_breakdown(
        self,
        analyses: List[PhantomAnalysis],
    ) -> dict:
        """Get breakdown of phantom positions."""
        breakdown = {}
        for a in analyses:
            breakdown[a.phantom_id] = {
                "name": a.phantom_name,
                "position": a.position.value,
                "conviction": a.conviction.value,
            }
        return breakdown

    def _empty_score(self) -> OpportunityScore:
        """Return empty score when no analyses provided."""
        return OpportunityScore(
            score=0.0,
            patterns_detected=[],
            primary_pattern=None,
            explanation="No analyses available",
            action_items=["No data to analyze"],
            risk_factors=[],
            phantom_breakdown={},
        )
