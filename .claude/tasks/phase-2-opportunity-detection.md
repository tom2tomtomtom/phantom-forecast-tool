# Phase 2: Opportunity Detection System

**Estimated Duration:** 2-3 weeks  
**Dependencies:** Phase 1 complete (phantom council working)  
**Status:** 📋 Planning

## Phase Objectives

1. Build market data enrichment pipeline (Perplexity + financial APIs)
2. Implement trigger detection system for opportunity scanning
3. Create opportunity scoring algorithm based on council patterns
4. Build automated daily scan workflow
5. Implement opportunity storage and historical tracking
6. Create opportunity dashboard UI

## Strategic Context

**Why This Phase:**
The phantom council is working, but it needs real market intelligence to spot opportunities. This phase transforms the council from "ask it anything" to "it finds opportunities for you."

**Core Insight:**
Opportunities emerge from **strategic disagreement** - when Buffett says "avoid" and Burry says "strong buy," that's not confusion, it's signal. This phase makes that signal actionable.

**Success Criteria:**
- Council can analyze any asset with current market context
- System auto-detects trigger conditions worth analyzing
- Daily scans produce ranked opportunity list
- UI clearly shows why each opportunity scored high

## Prerequisites Checklist

- [x] Phase 1 complete (phantom council functional)
- [x] 6 phantoms analyzing with distinct voices
- [x] Council synthesis working
- [x] Frontend dashboard built and connected
- [x] Perplexity API key obtained (in backend/.env)
- [ ] Financial data API selected (FMP, Alpha Vantage, or Polygon)
- [ ] Supabase database migrations ready
- [ ] Decision on caching strategy (Redis optional)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPPORTUNITY DETECTION FLOW                    │
└─────────────────────────────────────────────────────────────────┘

1. TRIGGER DETECTION (Morning Scan)
   ↓
   Market Screener → Statistical Anomalies
                  → Quality at Inflection
                  → Macro Shifts
                  → Consumer Behavior Changes
   ↓
   Triggered Assets List

2. DATA ENRICHMENT
   ↓
   For each triggered asset:
   ├── Perplexity: Recent news, sentiment, narrative
   ├── Financial API: Valuation metrics, price action
   ├── Moat Analysis: Competitive position data
   └── Macro Context: Fed policy, sector rotation
   ↓
   Enriched Market Context

3. PHANTOM COUNCIL ANALYSIS
   ↓
   Council analyzes with enriched context
   ├── Individual phantom analyses
   ├── Consensus detection
   ├── Disagreement identification
   └── Synthesis generation
   ↓
   Council Analysis Result

4. OPPORTUNITY SCORING
   ↓
   Score based on patterns:
   ├── High-conviction consensus (9/10)
   ├── Strategic disagreement (8/10)
   ├── Blind spot arbitrage (7/10)
   ├── Contrarian quality (9/10)
   └── Weak consensus (<5/10)
   ↓
   Scored Opportunities

5. STORAGE & NOTIFICATION
   ↓
   ├── Store in database (history tracking)
   ├── Update dashboard (real-time)
   └── Optional: Email/Slack notification
```

## Tasks

### 2.1 Market Data Enrichment Service

**Status:** 📋 Planned  
**Estimate:** 8 hours  
**Actual:** -

#### Requirements
- [ ] Perplexity service integration for news/sentiment
- [ ] Financial data API integration (valuation metrics)
- [ ] Price action data service
- [ ] Moat indicators calculator
- [ ] Macro context aggregator
- [ ] Data caching layer (prevent redundant API calls)

#### Files to Create
```
backend/src/services/
├── perplexity_service.py      # News and sentiment via Perplexity
├── financial_data_service.py  # Valuation metrics, financials
├── price_service.py           # Price action, technical data
├── moat_analyzer.py           # Competitive advantage indicators
└── macro_service.py           # Fed policy, sector rotation, cycles
```

#### Implementation Notes
```python
class MarketIntelligenceService:
    """
    Aggregates data from multiple sources for phantom analysis.
    """
    
    async def enrich_analysis_context(
        self,
        symbol: str,
        include_news: bool = True,
        include_fundamentals: bool = True,
        include_moat: bool = True,
        include_macro: bool = True
    ) -> EnrichedMarketContext:
        """
        Fetch and structure market intelligence for phantom consumption.
        
        Returns structured context optimized for LLM analysis.
        """
```

#### API Contracts
```python
# Perplexity request
{
  "query": "NVDA stock latest news earnings risks opportunities",
  "include_domains": ["wsj.com", "ft.com", "reuters.com"],
  "recency_filter": "month"
}

# Response format
{
  "summary": "2-3 paragraph synthesis of recent developments",
  "key_events": [
    {"date": "2024-12-10", "event": "Q4 earnings beat", "sentiment": "positive"},
    {"date": "2024-12-08", "event": "China export restrictions", "sentiment": "negative"}
  ],
  "analyst_sentiment": "Mixed - beat tempered by guidance concerns",
  "sources": [...]
}
```

#### Verification
- [ ] Can fetch news for any ticker
- [ ] Fundamental data returns complete metrics
- [ ] Price data includes 52-week range
- [ ] Moat indicators calculated correctly
- [ ] Macro context relevant to sector
- [ ] Response time <3s for full enrichment
- [ ] Caching prevents redundant API calls

---

### 2.2 Trigger Detection System

**Status:** 📋 Planned  
**Estimate:** 12 hours  
**Actual:** -

#### Requirements
- [ ] Statistical anomaly detector (Burry patterns)
- [ ] Quality inflection detector (Buffett patterns)
- [ ] Macro regime change detector (Dalio patterns)
- [ ] Consumer behavior detector (Lynch patterns)
- [ ] Market screener integration
- [ ] Configurable trigger thresholds

#### Files to Create
```
backend/src/core/
├── trigger_detector.py         # Main trigger detection orchestrator
├── triggers/
│   ├── __init__.py
│   ├── base.py                 # Base trigger class
│   ├── statistical.py          # Statistical anomalies
│   ├── quality.py              # Quality at inflection
│   ├── macro.py                # Macro regime changes
│   └── consumer.py             # Consumer behavior shifts
└── market_screener.py          # Screening engine
```

#### Implementation Notes
```python
class TriggerDetector:
    """
    Scans market for conditions worth phantom analysis.
    """
    
    triggers = [
        StatisticalAnomalyTrigger(),
        QualityInflectionTrigger(),
        MacroShiftTrigger(),
        ConsumerBehaviorTrigger(),
    ]
    
    async def scan_market(
        self,
        universe: Optional[List[str]] = None,  # None = scan full market
        trigger_types: Optional[List[str]] = None  # None = all triggers
    ) -> List[TriggeredAsset]:
        """
        Screen market for trigger conditions.
        
        Returns list of assets that triggered + why they triggered.
        """
```

#### Trigger Definitions
```python
# Statistical Anomaly (Burry)
TRIGGERS = {
    "massive_drawdown": {
        "condition": "price_change_30d < -20% AND fundamentals_stable",
        "phantom_relevance": ["burry", "buffett"],
        "priority": "high"
    },
    "valuation_dislocation": {
        "condition": "current_pe < (avg_5yr_pe * 0.5)",
        "phantom_relevance": ["burry", "buffett"],
        "priority": "high"
    },
    "short_squeeze_setup": {
        "condition": "short_interest > 30% AND quality_score > 7",
        "phantom_relevance": ["burry", "ackman"],
        "priority": "medium"
    }
}

# Quality Inflection (Buffett)
TRIGGERS = {
    "moat_expansion": {
        "condition": "market_share_increase AND pricing_power_up",
        "phantom_relevance": ["buffett", "munger"],
        "priority": "high"
    },
    "crisis_opportunity": {
        "condition": "sector_down > 15% AND company_moat_intact",
        "phantom_relevance": ["buffett", "ackman"],
        "priority": "high"
    }
}

# Macro Shift (Dalio)
TRIGGERS = {
    "regime_change": {
        "condition": "fed_policy_pivot OR inflation_trend_reversal",
        "phantom_relevance": ["dalio", "burry"],
        "priority": "high"
    },
    "cycle_turn": {
        "condition": "leading_indicators_bottoming",
        "phantom_relevance": ["dalio", "buffett"],
        "priority": "medium"
    }
}
```

#### Verification
- [ ] Detects drawdowns correctly
- [ ] Identifies valuation dislocations
- [ ] Recognizes moat expansions
- [ ] Catches macro regime changes
- [ ] Returns relevant phantom IDs
- [ ] Handles full market scans (<5 min)
- [ ] Configurable thresholds work

---

### 2.3 Enhanced Phantom System Prompts

**Status:** 📋 Planned  
**Estimate:** 4 hours  
**Actual:** -

#### Requirements
- [ ] Modify system prompt builder for market context
- [ ] Add trigger-specific context sections
- [ ] Include relevant data for each phantom type
- [ ] Format data for LLM consumption
- [ ] Test enhanced prompts maintain phantom voice

#### Files to Modify
```
backend/src/services/anthropic_service.py
```

#### Implementation Notes
```python
def build_enriched_system_prompt(
    phantom: PhantomDefinition,
    market_data: EnrichedMarketContext,
    trigger: TriggerType
) -> str:
    """
    Build system prompt with market context relevant to phantom.
    """
    
    base_prompt = build_phantom_system_prompt(phantom)
    
    # Add context sections based on phantom triggers
    context_sections = []
    
    if "moat" in phantom.trigger_patterns:
        context_sections.append(format_moat_section(market_data.moat_analysis))
    
    if "valuation" in phantom.trigger_patterns:
        context_sections.append(format_valuation_section(market_data.valuation))
    
    if "macro" in phantom.trigger_patterns:
        context_sections.append(format_macro_section(market_data.macro_context))
    
    # Include trigger reason
    trigger_context = f"""
## Why This Opportunity Was Flagged
Trigger Type: {trigger.type}
Trigger Reason: {trigger.reason}
Market Context: {trigger.market_context}
"""
    
    return f"{base_prompt}\n\n{'\n'.join(context_sections)}\n\n{trigger_context}"
```

#### Verification
- [ ] Buffett gets moat data
- [ ] Burry gets statistical data
- [ ] Dalio gets macro context
- [ ] Lynch gets consumer signals
- [ ] Phantom voices remain distinct
- [ ] Context doesn't overwhelm prompt

---

### 2.4 Opportunity Scoring Algorithm

**Status:** 📋 Planned  
**Estimate:** 6 hours  
**Actual:** -

#### Requirements
- [ ] Consensus pattern detector
- [ ] Disagreement pattern analyzer
- [ ] Conviction level aggregator
- [ ] Blind spot detector
- [ ] Opportunity score calculator
- [ ] Explanation generator

#### Files to Create
```
backend/src/core/
├── opportunity_scorer.py       # Main scoring logic
└── scoring_patterns.py         # Pattern definitions
```

#### Implementation Notes
```python
class OpportunityScorer:
    """
    Scores opportunities based on council analysis patterns.
    """
    
    def score_opportunity(
        self,
        council: CouncilAnalysis,
        market_data: EnrichedMarketContext,
        trigger: TriggerType
    ) -> OpportunityScore:
        """
        Calculate opportunity score from council patterns.
        
        Score ranges:
        9-10: Exceptional - rare high-conviction consensus or perfect disagreement pattern
        7-8: Strong - clear opportunity signal from pattern
        5-6: Moderate - interesting but needs more research
        3-4: Weak - conflicting signals or low conviction
        1-2: Pass - consensus uncertainty or negative
        """
        
        patterns = {
            "high_conviction_consensus": self._check_consensus_strength(council),
            "strategic_disagreement": self._check_disagreement_pattern(council),
            "blind_spot_arbitrage": self._check_blind_spot_opportunity(council),
            "contrarian_quality": self._check_contrarian_quality(council, market_data),
            "catalyst_alignment": self._check_catalyst_alignment(council, trigger)
        }
        
        score = self._calculate_score(patterns)
        explanation = self._generate_explanation(patterns, council)
        
        return OpportunityScore(
            score=score,
            patterns_detected=patterns,
            explanation=explanation,
            action_items=self._generate_action_items(patterns),
            risk_factors=self._extract_risk_factors(council)
        )
```

#### Scoring Patterns
```python
# Pattern 1: High-Conviction Consensus (9/10)
def _check_consensus_strength(council):
    high_conviction_count = sum(
        1 for a in council.analyses 
        if a.conviction == Conviction.HIGH
    )
    
    if high_conviction_count >= 4 and council.consensus:
        return {
            "detected": True,
            "score_impact": 9.0,
            "insight": "Rare agreement across diverse philosophies - strong signal"
        }

# Pattern 2: Strategic Disagreement (8/10)
def _check_disagreement_pattern(council):
    # Buffett avoid + Burry strong buy = value/growth dislocation
    buffett = next((a for a in council.analyses if a.phantom_id == "buffett"), None)
    burry = next((a for a in council.analyses if a.phantom_id == "burry"), None)
    
    if buffett and burry:
        if buffett.position == Position.AVOID and burry.conviction == Conviction.HIGH:
            return {
                "detected": True,
                "score_impact": 8.0,
                "insight": "Classic value vs growth tension - market uncertainty creating entry"
            }

# Pattern 3: Contrarian Quality (9/10)
def _check_contrarian_quality(council, market_data):
    # Market bearish + quality phantoms neutral/bullish = crisis opportunity
    if market_data.sentiment == "bearish":
        quality_phantoms = [a for a in council.analyses 
                           if a.phantom_id in ["buffett", "munger"]]
        
        if any(p.position >= Position.NEUTRAL for p in quality_phantoms):
            return {
                "detected": True,
                "score_impact": 9.0,
                "insight": "Quality asset at distressed pricing - classic Buffett opportunity"
            }
```

#### Verification
- [ ] High-conviction consensus scores 9+
- [ ] Strategic disagreement scores 7-8
- [ ] Weak consensus scores <5
- [ ] Explanations are clear and actionable
- [ ] Action items specific to pattern
- [ ] Risk factors properly identified

---

### 2.5 Opportunity Storage & Tracking

**Status:** 📋 Planned  
**Estimate:** 4 hours  
**Actual:** -

#### Requirements
- [ ] Database migrations for opportunity tables
- [ ] Opportunity model (SQLAlchemy)
- [ ] Storage service for persisting opportunities
- [ ] Historical tracking of opportunity scores
- [ ] Performance tracking (how did opportunities perform)

#### Files to Create
```
backend/supabase/migrations/
└── 004_opportunities.sql       # Opportunities schema

backend/src/models/
└── opportunity.py              # Opportunity model

backend/src/services/
└── opportunity_service.py      # CRUD operations
```

#### Database Schema
```sql
-- Opportunities table
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_reason TEXT,
    
    -- Opportunity metadata
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    opportunity_score DECIMAL(3,1) NOT NULL CHECK (opportunity_score >= 0 AND opportunity_score <= 10),
    
    -- Council analysis
    council_analysis JSONB NOT NULL,  -- Full council result
    consensus_position VARCHAR(20),
    consensus_strength VARCHAR(20),
    key_disagreements TEXT[],
    
    -- Scoring details
    patterns_detected JSONB,  -- Which patterns triggered
    explanation TEXT NOT NULL,
    action_items TEXT[],
    risk_factors TEXT[],
    
    -- Market context at detection
    market_context JSONB,  -- Price, valuation, news at detection time
    
    -- Performance tracking
    entry_price DECIMAL(10,2),
    current_price DECIMAL(10,2),
    performance DECIMAL(5,2),  -- % return if acted on
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_opportunities_symbol ON opportunities(symbol);
CREATE INDEX idx_opportunities_score ON opportunities(opportunity_score DESC);
CREATE INDEX idx_opportunities_detected_at ON opportunities(detected_at DESC);
CREATE INDEX idx_opportunities_trigger ON opportunities(trigger_type);

-- Opportunity performance view
CREATE VIEW opportunity_performance AS
SELECT 
    trigger_type,
    AVG(opportunity_score) as avg_score,
    AVG(performance) as avg_performance,
    COUNT(*) as count,
    COUNT(*) FILTER (WHERE performance > 0) as profitable_count
FROM opportunities
WHERE performance IS NOT NULL
GROUP BY trigger_type;
```

#### Verification
- [ ] Opportunities persist correctly
- [ ] JSON fields store full council result
- [ ] Historical queries performant
- [ ] Performance tracking updates
- [ ] Views calculate correctly

---

### 2.6 Daily Scan Automation

**Status:** 📋 Planned  
**Estimate:** 8 hours  
**Actual:** -

#### Requirements
- [ ] Scheduled job runner (APScheduler or similar)
- [ ] Daily scan orchestrator
- [ ] Watchlist management (which symbols to scan)
- [ ] Scan results emailer (optional)
- [ ] Admin endpoint to trigger manual scans

#### Files to Create
```
backend/src/jobs/
├── __init__.py
├── scheduler.py                # Job scheduler setup
└── daily_scan.py               # Daily scan job

backend/src/api/routes/
└── scan.py                     # Manual scan endpoints
```

#### Implementation Notes
```python
# Daily scan job
async def run_daily_opportunity_scan():
    """
    Automated morning scan for opportunities.
    
    Runs at 8:00 AM ET (before market open):
    1. Screen market for triggers
    2. Enrich triggered assets with market data
    3. Run phantom council on each
    4. Score opportunities
    5. Store top 20 in database
    6. Email results (optional)
    """
    
    logger.info("Starting daily opportunity scan...")
    
    # 1. Detect triggers
    trigger_detector = TriggerDetector()
    triggered_assets = await trigger_detector.scan_market()
    logger.info(f"Found {len(triggered_assets)} triggered assets")
    
    opportunities = []
    
    for asset in triggered_assets:
        # 2. Enrich with market data
        market_data = await market_intelligence.enrich_context(asset.symbol)
        
        # 3. Run council analysis
        council = await analyze_with_council(
            asset=asset.symbol,
            context=market_data,
            phantom_ids=select_relevant_phantoms(asset.trigger_type)
        )
        
        # 4. Score opportunity
        score = opportunity_scorer.score(council, market_data, asset.trigger)
        
        if score.score >= 6.0:  # Only store decent opportunities
            opportunities.append(score)
    
    # 5. Store top 20
    opportunities.sort(key=lambda x: x.score, reverse=True)
    await opportunity_service.store_batch(opportunities[:20])
    
    # 6. Email summary (optional)
    if settings.email_enabled:
        await email_service.send_daily_digest(opportunities[:10])
    
    logger.info(f"Daily scan complete. Stored {len(opportunities[:20])} opportunities")
```

#### API Endpoints
```python
# Manual scan endpoint
@router.post("/scan/manual")
async def manual_scan(
    symbols: Optional[List[str]] = None,
    trigger_types: Optional[List[str]] = None
) -> ScanResult:
    """Trigger manual opportunity scan"""

# Get scan results
@router.get("/scan/results")
async def get_scan_results(
    date: Optional[date] = None,
    min_score: float = 6.0
) -> List[OpportunityScore]:
    """Retrieve opportunities from a specific scan"""

# Get top opportunities
@router.get("/opportunities/top")
async def get_top_opportunities(
    limit: int = 20,
    days: int = 7
) -> List[OpportunityScore]:
    """Get top opportunities from last N days"""
```

#### Verification
- [ ] Scheduler runs at configured time
- [ ] Manual scans work via API
- [ ] Scan completes in reasonable time (<30 min for full market)
- [ ] Results stored in database
- [ ] Email notifications work (if enabled)
- [ ] Errors logged properly

---

### 2.7 Opportunity Dashboard UI

**Status:** 📋 Planned  
**Estimate:** 12 hours  
**Actual:** -

#### Requirements
- [ ] Opportunity list view (sortable, filterable)
- [ ] Opportunity detail page
- [ ] Council analysis visualization
- [ ] Disagreement pattern display
- [ ] Historical performance charts
- [ ] Manual scan trigger UI

#### Files to Create
```
frontend/src/app/
├── opportunities/
│   ├── page.tsx                # Opportunity list
│   └── [id]/
│       └── page.tsx            # Opportunity detail

frontend/src/components/opportunity/
├── opportunity-card.tsx        # List item card
├── opportunity-detail.tsx      # Full detail view
├── council-visualization.tsx   # Council analysis viz
├── score-breakdown.tsx         # Score explanation
└── pattern-display.tsx         # Detected patterns

frontend/src/lib/api/
└── opportunities.ts            # API client
```

#### UI Components

**Opportunity Card:**
```typescript
<OpportunityCard
  opportunity={{
    symbol: "NVDA",
    score: 8.5,
    trigger: "valuation_dislocation",
    consensus: "mixed",
    keyInsight: "Buffett avoid vs Burry strong buy - growth/value tension",
    detectedAt: "2024-12-13T08:00:00Z"
  }}
/>
```

**Council Visualization:**
```
┌─────────────────────────────────────────────────────────────┐
│                    PHANTOM COUNCIL ANALYSIS                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Buffett ████████░░ NEUTRAL (Medium)                        │
│  "Can't predict tech moat 10 years out"                     │
│                                                              │
│  Burry  ██████████ STRONG BUY (High)                        │
│  "Statistical mispricing + quality fundamentals"            │
│                                                              │
│  Dalio  ███████░░░ BULLISH (Medium)                         │
│  "Secular trend + favorable macro"                          │
│                                                              │
│  Lynch  ████████░░ BULLISH (Medium)                         │
│  "Consumer demand explosive"                                │
│                                                              │
│  Consensus: MIXED - Interesting disagreement pattern        │
│  Score: 8.5/10 - Strategic disagreement opportunity         │
└─────────────────────────────────────────────────────────────┘
```

**Pattern Display:**
```typescript
<PatternDisplay
  patterns={[
    {
      type: "strategic_disagreement",
      detected: true,
      impact: 8.0,
      insight: "Value vs growth tension reveals market uncertainty"
    },
    {
      type: "blind_spot_arbitrage",
      detected: false
    }
  ]}
/>
```

#### Verification
- [ ] Opportunity list loads and sorts
- [ ] Filters work (score, trigger, date)
- [ ] Detail page shows full council
- [ ] Visualizations clear and helpful
- [ ] Manual scan works from UI
- [ ] Responsive on mobile
- [ ] Loading states smooth

---

### 2.8 Quick-Win MVP Implementation

**Status:** 📋 Planned  
**Estimate:** 4 hours  
**Actual:** -

#### Requirements
- [ ] Simple watchlist scanner (before full market scan)
- [ ] Perplexity-only enrichment (defer other APIs)
- [ ] Basic scoring (high conviction consensus only)
- [ ] Simple results page

#### Files to Create
```
backend/src/api/routes/
└── quick_scan.py               # MVP scan endpoint

frontend/src/app/
└── quick-scan/
    └── page.tsx                # Simple scan UI
```

#### Implementation Notes
```python
@router.post("/quick-scan")
async def quick_opportunity_scan(
    symbols: List[str],
    context_source: str = "perplexity"
) -> List[QuickOpportunity]:
    """
    Quick opportunity scan on a watchlist.
    
    MVP version:
    - Takes symbol list (no trigger detection)
    - Uses Perplexity only (no financial APIs)
    - Simple scoring (consensus strength only)
    - Returns ranked list
    """
    
    opportunities = []
    
    for symbol in symbols:
        # Get latest news
        news = await perplexity_client.search(
            f"{symbol} stock recent news earnings risks"
        )
        
        # Run council
        council = await analyze_with_council(
            asset=symbol,
            context=news.summary
        )
        
        # Simple scoring
        score = calculate_simple_score(council)
        
        opportunities.append({
            "symbol": symbol,
            "score": score,
            "consensus": council.consensus,
            "insight": council.synthesis,
            "high_conviction_count": sum(
                1 for a in council.analyses 
                if a.conviction == Conviction.HIGH
            )
        })
    
    return sorted(opportunities, key=lambda x: x["score"], reverse=True)
```

#### Verification
- [ ] Scans watchlist successfully
- [ ] Returns results in <30s for 10 symbols
- [ ] Scores make intuitive sense
- [ ] UI displays results clearly
- [ ] Can test immediately after deployment

---

## Phase Completion Criteria

### Technical Criteria
- [ ] All tasks marked complete
- [ ] All verifications passing
- [ ] No TypeScript/Python errors
- [ ] API response times acceptable (<5s per analysis)
- [ ] Database queries optimized
- [ ] Error handling comprehensive

### Functional Criteria
- [ ] Daily scan runs successfully
- [ ] Trigger detection identifies real opportunities
- [ ] Scoring produces sensible rankings
- [ ] UI clearly displays opportunities
- [ ] Historical tracking working
- [ ] Manual scans functional

### Quality Criteria
- [ ] Phantom voices remain distinct with enriched context
- [ ] Opportunity explanations actionable
- [ ] False positive rate acceptable (<50%)
- [ ] Top-scored opportunities actually interesting
- [ ] Performance tracking implemented

### Documentation Criteria
- [ ] STATUS.md updated
- [ ] New ADRs for major decisions
- [ ] API documentation complete
- [ ] User guide for opportunity dashboard

## Phase Sign-off

**Completed:** [Date]  
**Signed off by:** [Name]  
**Notes:**

## Dependencies & Blockers

### External Dependencies
- [ ] Perplexity API access & budget
- [ ] Financial data API selection & setup
- [ ] Email service (SendGrid, AWS SES, or similar) - optional
- [ ] Scheduler infrastructure (APScheduler or cron)

### Internal Dependencies
- [x] Phase 1 phantom council working
- [ ] Database migration strategy finalized
- [ ] Caching strategy decided (Redis optional)

### Known Risks
1. **API Costs:** Perplexity + Financial APIs + Anthropic could get expensive with daily full-market scans
   - *Mitigation:* Start with watchlist, add caching, batch requests
2. **Trigger False Positives:** May flag too many "opportunities" that aren't real
   - *Mitigation:* Tune thresholds, add minimum score filter, track performance
3. **Prompt Bloat:** Enriched context might make prompts too long
   - *Mitigation:* Selective context based on phantom triggers, summarize where possible

## Future Enhancements (Phase 3)

- Real-time opportunity alerts (WebSocket)
- Portfolio tracking (track actual positions vs opportunities)
- Backtesting (test historical opportunities)
- Custom trigger creation (user-defined patterns)
- Multi-asset opportunity detection (pairs, sectors)
- Opportunity "aging" (track how opportunities evolve)
