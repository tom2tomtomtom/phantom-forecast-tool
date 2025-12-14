# Architectural Decision Records

## ADR-001: Phantom System as Separate Python Service

**Date:** 2024-12-13
**Status:** Accepted
**Context:** Need to decide whether phantom reasoning runs in Next.js API routes or separate service

**Decision:** Build phantom system as standalone Python FastAPI service

**Reasoning:**
- Anthropic SDK better supported in Python
- Phantom prompt engineering requires rapid iteration outside Next.js rebuild cycle
- Allows independent scaling of compute-intensive phantom reasoning
- Python ecosystem better for AI/ML experimentation
- Can evolve into standalone service for other tools

**Consequences:**
- Frontend becomes thin client
- Need to handle cross-origin requests
- Easier to test phantom logic in isolation
- Can deploy frontend/backend independently

---

## ADR-002: JSON Files for Phantom Definitions vs. Database

**Date:** 2024-12-13
**Status:** Accepted
**Context:** How to store phantom persona definitions and memories

**Decision:** Store phantom definitions as JSON files in version control, not database

**Reasoning:**
- Phantom definitions are code, not data - they define behavior
- Version control provides history and rollback
- Easy to review changes in PR/commit diffs
- Fast iteration without database migrations
- Can be loaded at startup for performance
- Easy to duplicate/fork phantoms for experiments

**Consequences:**
- Can't modify phantoms at runtime (this is good - prevents drift)
- Requires service restart for phantom updates (acceptable for experiment)
- Git diffs show evolution of phantom strategic judgment
- Easy to A/B test phantom variations

---

## ADR-003: Sequential vs. Parallel Phantom Analysis

**Date:** 2024-12-13
**Status:** Accepted
**Context:** Should phantoms analyze simultaneously or see each other's takes?

**Decision:** Phase 1 - Sequential with context isolation. Phase 2 - Debate mode

**Reasoning:**
Phase 1 (Current):
- Each phantom analyzes independently without seeing others
- Prevents groupthink and anchoring
- Pure philosophical diversity
- Easier to implement

Phase 2 (Future):
- Phantoms can "debate" - respond to each other's analyses
- More realistic investment committee dynamic
- Tests phantom ability to defend positions
- Computationally expensive but intellectually interesting

**Consequences:**
- Phase 1 gives baseline phantom distinctiveness
- Can compare Phase 1 (isolation) vs Phase 2 (debate) outputs
- Need to design debate orchestration carefully to avoid LLM repetition

---

## ADR-004: Real-Time vs. Historical Data Priority

**Date:** 2024-12-13
**Status:** Accepted
**Context:** Tool could focus on live trading signals or historical pattern analysis

**Decision:** Optimize for real-time analysis with historical storage, not backtesting

**Reasoning:**
- Experimental goal is testing phantom judgment, not trading system
- Real-time forces phantoms to handle novel situations
- Backtesting invites overfitting phantom memories to past data
- More valuable to see how phantoms respond to current uncertainty
- Historical storage enables learning but not the primary use case

**Consequences:**
- Less focus on prediction accuracy metrics
- More focus on strategic disagreement quality
- Can add backtesting later if phantoms prove valuable
- Database design prioritizes write speed over complex queries

---

## ADR-005: Perplexity for Market Data vs. Traditional APIs

**Date:** 2024-12-13
**Status:** Accepted
**Context:** How to gather market intelligence beyond raw price data

**Decision:** Perplexity as primary intelligence source, Alpha Vantage for price data

**Reasoning:**
- Perplexity provides synthesized market context, not just data points
- Can ask natural language questions about market conditions
- Reduces need for complex data aggregation logic
- Alpha Vantage free tier sufficient for price/fundamental data
- Total cost < $50/month for experimentation

**Consequences:**
- Dependent on Perplexity API availability
- Need fallback for price data (Yahoo Finance API)
- Richer context for phantoms to analyze
- Less data engineering, more AI orchestration

---

## ADR-006: Synthesis as Separate AI Call vs. Rule-Based

**Date:** 2024-12-13
**Status:** Accepted
**Context:** How to generate synthesis across phantom analyses

**Decision:** Synthesis via separate Claude call with all phantom outputs as context

**Reasoning:**
- LLM better at identifying non-obvious patterns than rules
- Can ask synthesis to specifically look for blind spots
- Flexible - can change synthesis prompting without code changes
- Tests AI's ability to meta-analyze AI outputs
- Cost minimal (one extra Claude call per analysis)

**Consequences:**
- Need clear synthesis prompt engineering
- Risk of synthesis being too bland/diplomatic
- Can instruct synthesis to be provocative about disagreements
- Additional 2-3 seconds to analysis time

---

## ADR-007: TypeScript Strict Mode Throughout

**Date:** 2024-12-13
**Status:** Accepted
**Context:** Type safety level for frontend

**Decision:** TypeScript strict mode enabled, no any types allowed

**Reasoning:**
- Phantom responses have complex nested structures
- Type safety prevents runtime errors in UI
- Better developer experience with autocomplete
- Forces explicit handling of undefined/null cases
- Small upfront cost, large long-term benefit

**Consequences:**
- Need comprehensive type definitions for API responses
- Zod schemas for runtime validation + type inference
- Slightly slower initial development
- Much faster debugging and refactoring

---

## ADR-008: Single vs. Multiple Markets Per Analysis

**Date:** 2024-12-13
**Status:** Accepted
**Context:** Should users analyze one asset at a time or compare multiple?

**Decision:** Phase 1 - Single asset analysis. Phase 2 - Comparative analysis

**Reasoning:**
Phase 1:
- Simpler to implement and test
- Clearer feedback on phantom quality
- Easier to understand UI

Phase 2:
- Comparative analysis ("AAPL vs MSFT") more valuable
- Phantoms could rank opportunities
- More realistic investment decision context

**Consequences:**
- Phase 1 proves phantom concept
- Phase 2 requires multi-asset context in prompts
- Database supports both (market_data is single asset)

---

## ADR-009: No Authentication in Phase 1

**Date:** 2024-12-13
**Status:** Accepted
**Context:** Whether to require user accounts

**Decision:** No authentication for initial experiment, add later if valuable

**Reasoning:**
- Friction reduces experimentation velocity
- Not handling sensitive user data yet
- Can add Supabase auth later if becomes multi-user tool
- Allows rapid testing with colleagues

**Consequences:**
- No usage tracking per user
- Can't save favorite phantoms/markets
- Database queries simpler
- Anyone with URL can access (fine for personal experiment)

---

## ADR-010: Phantom Memory Structure - Narrative vs. Structured Data

**Date:** 2024-12-13
**Status:** Accepted
**Context:** How to format phantom memories for optimal strategic reasoning

**Decision:** Narrative format with structured metadata

**Reasoning:**
- Claude processes narrative context better than key-value pairs
- Story format embeds causal reasoning
- Structured fields (context/decision/outcome) provide consistency
- Mimics how humans actually remember strategic lessons
- Easier to write/review than pure data structures

**Consequences:**
- Phantom JSON files more readable
- Can review phantom quality by reading memories
- Easier to add new phantoms - just write stories
- Memory quality directly impacts phantom judgment quality

---

## Phase 2: Opportunity Detection System

## ADR-011: Trigger-Based Scanning vs. Continuous Monitoring

**Date:** 2024-12-14
**Status:** Accepted
**Context:** How to identify which assets warrant phantom council analysis

**Decision:** Trigger-based scanning with phantom-specific pattern matching

**Reasoning:**
- Not every asset needs full council analysis (expensive)
- Triggers filter signal from noise before expensive AI calls
- Different phantoms trigger on different patterns (moats vs statistical anomalies)
- Reduces API costs by 90%+ (scan 3000 → analyze 100)
- Matches how real investors scan markets

**Trigger Categories:**
- Statistical anomalies (Burry): Valuation dislocations, drawdowns
- Quality inflections (Buffett): Moat expansion, crisis opportunities
- Macro shifts (Dalio): Regime changes, cycle turns
- Consumer behavior (Lynch): Viral adoption, category creation

**Consequences:**
- Need robust trigger detection system
- May miss opportunities that don't fit patterns
- Can tune trigger sensitivity over time
- Creates data on which triggers produce best opportunities

---

## ADR-012: Enriched Context vs. Raw Data for Phantoms

**Date:** 2024-12-14
**Status:** Accepted
**Context:** What data format to feed phantom council for opportunity analysis

**Decision:** Enriched market intelligence (synthesized) over raw data dumps

**Reasoning:**
- Phantoms reason better with narrative context than CSV data
- Perplexity synthesizes news → saves phantom token budget
- Financial APIs provide clean metrics vs manual parsing
- Quality of context directly impacts analysis quality
- Can include phantom-specific data (moats for Buffett, macro for Dalio)

**Implementation:**
```python
EnrichedContext:
  - news_summary (Perplexity synthesis)
  - valuation_metrics (FMP API)
  - price_action (Alpha Vantage)
  - moat_indicators (calculated)
  - macro_environment (aggregated)
  - trigger_reason (why flagged)
```

**Consequences:**
- Extra API calls for enrichment (cost: ~$3/symbol)
- Slower but higher quality analysis
- Can A/B test enriched vs minimal context
- Makes phantom reasoning traceable (given X data → Y conclusion)

---

## ADR-013: AI-Based Opportunity Scoring vs. Rule-Based

**Date:** 2024-12-14
**Status:** Accepted
**Context:** How to score and rank opportunities from council analysis

**Decision:** Pattern-based heuristics (not AI) for opportunity scoring

**Reasoning:**
- Opportunity signals are pattern-based (consensus, disagreement, etc.)
- Deterministic scoring is transparent and tunable
- AI scoring adds cost without clear benefit
- Humans understand heuristic rules better than AI black boxes
- Can always add AI scoring layer later if needed

**Scoring Patterns:**
1. High-conviction consensus (9/10) - Rare agreement across diverse phantoms
2. Strategic disagreement (8/10) - Buffett/Burry opposing = market dislocation
3. Contrarian quality (9/10) - Quality assets at distressed pricing
4. Blind spot arbitrage (7/10) - Market overpricing known unknowns

**Consequences:**
- Need to define scoring patterns explicitly
- Can test pattern effectiveness over time
- Transparent to users why score is 8 vs 6
- Risk of missing non-obvious scoring patterns

---

## ADR-014: Daily Batch Scanning vs. Real-Time Streaming

**Date:** 2024-12-14
**Status:** Accepted
**Context:** When to run opportunity detection

**Decision:** Daily batch scan before market open, with manual scan option

**Reasoning:**
- Market conditions don't change minute-to-minute for this use case
- Daily scan produces manageable opportunity list (~20)
- Batch processing more efficient than streaming
- Matches natural decision-making rhythm (review in morning)
- Can add real-time alerts later for high-score opportunities

**Schedule:**
- Automated: 8:00 AM ET daily (before market open)
- Manual: On-demand via API endpoint
- Storage: Top 20 opportunities per scan
- Notification: Email digest (optional)

**Consequences:**
- Miss intraday opportunities (acceptable for strategic analysis)
- Predictable API cost (daily batch vs unpredictable streaming)
- Can review opportunities before market chaos
- Storage requirements modest (20 opportunities/day)

---

## ADR-015: Opportunity Storage - Full History vs. Recent Only

**Date:** 2024-12-14
**Status:** Accepted
**Context:** How much opportunity history to retain

**Decision:** Store all opportunities indefinitely for performance tracking

**Reasoning:**
- Opportunity quality unknowable without outcome data
- Historical analysis reveals which triggers/patterns work
- Disk is cheap, strategic learning is valuable
- Can track "phantom batting average" over time
- Enables future ML on what makes good opportunities

**Database:**
- Full council analysis (JSONB)
- Market context at detection time
- Opportunity score + patterns
- Performance tracking (entry vs current price)

**Consequences:**
- Database grows ~2MB/day (acceptable)
- Enables rich analytics later
- Can identify false positive patterns
- Need periodic pruning of low-quality opportunities (<5 score)

---

## ADR-016: APScheduler vs. External Cron for Automation

**Date:** 2024-12-14
**Status:** Accepted
**Context:** How to schedule daily opportunity scans

**Decision:** APScheduler in FastAPI application (not external cron)

**Reasoning:**
- Railway doesn't provide cron access
- APScheduler is Python-native, async-compatible
- Programmatic control (can pause/resume via API)
- No separate infrastructure needed
- Works identically in dev and production

**Configuration:**
```python
scheduler = AsyncIOScheduler()
scheduler.add_job(
    run_daily_scan,
    trigger=CronTrigger(hour=8, timezone="America/New_York"),
    id="daily_scan"
)
```

**Consequences:**
- Scheduler requires FastAPI process running
- Need proper shutdown handling
- Can trigger manual scans via endpoint
- Easier debugging than external cron

---

## ADR-17: Watchlist vs. Full Market Scanning

**Date:** 2024-12-14
**Status:** Accepted
**Context:** Which assets to scan for opportunities

**Decision:** Start with configurable watchlist, scale to full market if valuable

**Reasoning:**
- Full market scan = 3000+ symbols = expensive
- Watchlist (S&P 500 or custom 100) = manageable cost
- Can test opportunity quality with smaller set
- Easier to validate triggers with known companies
- Full market scanning available, just disabled by default

**Cost Comparison:**
- Watchlist (100 symbols): ~$10/day
- Full market (3000 symbols): ~$210/day

**Decision:** Start watchlist, upgrade if proves valuable

**Consequences:**
- May miss opportunities in small caps
- Lower API costs during testing
- Faster scan completion (<10 min vs 30+ min)
- Can add custom watchlists (tech, value, growth, etc.)

---

## ADR-018: Redis Caching - Optional vs. Required

**Date:** 2024-12-14
**Status:** Accepted
**Context:** Whether to cache market data API responses

**Decision:** Redis caching optional (not required for Phase 2)

**Reasoning:**
- Daily scans run once → caching benefit minimal
- Market data changes daily → cache short-lived
- Adds infrastructure complexity
- Can add later if API costs exceed budget

**When to add Redis:**
- If running multiple scans per day
- If manual scans frequent
- If API rate limits become issue

**Consequences:**
- Simpler deployment initially
- Slightly higher API costs (acceptable)
- Can add caching in Phase 3 if needed
- Railway Redis add-on ready if needed

---

## ADR-019: Phantom-Specific Context vs. Universal Context

**Date:** 2024-12-14
**Status:** Accepted
**Context:** Should each phantom get customized market data?

**Decision:** Selective context enrichment based on phantom triggers

**Reasoning:**
- Buffett doesn't need technical indicators
- Burry doesn't need brand strength scores
- Customized context = smaller prompts = faster + cheaper
- Phantoms focus on what they actually analyze

**Implementation:**
```python
if "moat" in phantom.trigger_patterns:
    context.moat_analysis = calculate_moat_indicators()
if "valuation" in phantom.trigger_patterns:
    context.valuation = fetch_valuation_metrics()
if "macro" in phantom.trigger_patterns:
    context.macro = aggregate_macro_data()
```

**Consequences:**
- Need phantom-specific prompt builders
- Reduces prompt bloat
- Maintains phantom focus on relevant signals
- Slightly more complex enrichment logic

---

## ADR-020: Opportunity Explanations - AI vs. Template

**Date:** 2024-12-14
**Status:** Accepted
**Context:** How to explain opportunity scores to users

**Decision:** Template-based explanations with pattern-specific messaging

**Reasoning:**
- Explanation patterns predictable (consensus, disagreement, etc.)
- Templates faster and cheaper than AI generation
- Users understand consistent messaging better
- Can refine templates based on user feedback

**Example:**
```python
if pattern == "high_conviction_consensus":
    explanation = f"Rare agreement across {count} diverse phantoms signals strong opportunity. {phantoms} all identify {key_factor}."
```

**Consequences:**
- Explanations may feel formulaic
- Faster generation (<1ms vs 2s for AI)
- Transparent and predictable
- Can add AI explanations later for edge cases

---

## Open Questions

### Q1: How many phantoms is optimal?
Current plan: 5-7. Too few = insufficient diversity. Too many = noise.
**Decision needed:** After testing Phase 1 with 6 phantoms
**Status:** 6 phantoms working well, no changes needed

### Q2: Should phantoms have "moods" or market-condition filters?
e.g., Buffett more active in bear markets. Burry more active in bubbles.
**Decision needed:** After observing phantom consistency across conditions

### Q3: Can phantoms learn from forecast accuracy?
Technically possible to update phantom memories based on outcomes.
**Decision needed:** Philosophical - does this make them more/less valuable?

### Q4: Should synthesis provide actionable trade recommendations?
Currently focused on insights. Could add position sizing, entry points, etc.
**Decision needed:** After regulatory/liability considerations

### Q5: How to handle opportunity "aging"? (Phase 2)
Opportunities become stale as market conditions change. Re-scan? Archive?
**Decision needed:** After observing opportunity lifecycle

### Q6: Should we track which phantoms are "right" more often? (Phase 2)
Could weight council by historical accuracy. But risks overfitting.
**Decision needed:** After collecting outcome data

### Q7: Email notifications - who gets them and when? (Phase 2)
Daily digest? High-score alerts only? Configurable?
**Decision needed:** After user testing feedback

### Q8: Full market scan - worth the cost? (Phase 2)
$210/month for comprehensive scanning. Value vs watchlist?
**Decision needed:** After 1 month of watchlist results
