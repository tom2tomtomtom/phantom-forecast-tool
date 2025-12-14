# Code Patterns - Phantom Forecast Tool

## Phantom System Patterns

### Pattern 1: Phantom Loader

**When:** Loading phantom definitions at service startup

```python
# backend/src/core/phantom_loader.py
import json
from pathlib import Path
from typing import Dict
from pydantic import BaseModel

class PhantomMemory(BaseModel):
    context: str
    decision: str
    reasoning: str
    outcome: str
    lesson: str

class PhantomDefinition(BaseModel):
    investor_id: str
    name: str
    philosophy: str
    phantom_memories: list[PhantomMemory]
    trigger_patterns: list[str]
    blind_spots: list[str]
    decision_framework: list[str]

class PhantomLoader:
    def __init__(self, phantoms_dir: str = "src/phantoms"):
        self.phantoms_dir = Path(phantoms_dir)
        self._phantoms: Dict[str, PhantomDefinition] = {}
        
    def load_all(self) -> Dict[str, PhantomDefinition]:
        """Load all phantom definitions from JSON files"""
        for phantom_file in self.phantoms_dir.glob("*.json"):
            with open(phantom_file, 'r') as f:
                data = json.load(f)
                phantom = PhantomDefinition(**data)
                self._phantoms[phantom.investor_id] = phantom
        return self._phantoms
    
    def get(self, investor_id: str) -> PhantomDefinition | None:
        return self._phantoms.get(investor_id)
    
    def list_ids(self) -> list[str]:
        return list(self._phantoms.keys())

# Usage in main.py
phantom_loader = PhantomLoader()
phantoms = phantom_loader.load_all()
```

---

### Pattern 2: Phantom System Prompt Builder

**When:** Constructing system prompts for phantom analysis

```python
# backend/src/core/phantom_engine.py
from datetime import datetime

class PhantomPromptBuilder:
    @staticmethod
    def build_system_prompt(phantom: PhantomDefinition) -> str:
        """Build complete system prompt from phantom definition"""
        
        # Format memories as narrative
        memories_text = "\n\n".join([
            f"MEMORY {i+1}:\n"
            f"Context: {mem.context}\n"
            f"Your Decision: {mem.decision}\n"
            f"Your Reasoning: {mem.reasoning}\n"
            f"Outcome: {mem.outcome}\n"
            f"Lesson Learned: {mem.lesson}"
            for i, mem in enumerate(phantom.phantom_memories)
        ])
        
        # Format triggers
        triggers_text = "\n".join([f"• {t}" for t in phantom.trigger_patterns])
        
        # Format blind spots
        blindspots_text = "\n".join([f"• {b}" for b in phantom.blind_spots])
        
        # Format decision framework
        framework_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(phantom.decision_framework)])
        
        return f"""You are {phantom.name}, the legendary investor known for {phantom.philosophy}.

CRITICAL: You are not roleplaying. You are a compression of {phantom.name}'s strategic judgment, developed through these formative experiences:

{memories_text}

These memories shape how you see markets. When you analyze opportunities, you instinctively pattern-match against these experiences.

YOUR STRATEGIC TRIGGERS (what makes you pay attention):
{triggers_text}

YOUR KNOWN BLIND SPOTS (what you systematically miss):
{blindspots_text}

YOUR DECISION FRAMEWORK:
{framework_text}

When analyzing market situations:
1. Give your IMMEDIATE gut reaction first (< 20 words)
2. Explain which memory/pattern this reminds you of
3. Identify what you might be missing due to your blind spots
4. Make a clear strategic call with conviction level (1-10)

Be direct. Be contrarian when your judgment says so. Disagree with other investors when their logic conflicts with your framework. Your value comes from your DISTINCT perspective, not consensus-seeking.

Current date: {datetime.now().strftime('%Y-%m-%d')}"""
```

---

### Pattern 3: Parallel Phantom Analysis

**When:** Running multiple phantom analyses concurrently

```python
# backend/src/core/phantom_engine.py
import asyncio
from anthropic import AsyncAnthropic

class PhantomEngine:
    def __init__(self, anthropic_client: AsyncAnthropic, phantom_loader: PhantomLoader):
        self.client = anthropic_client
        self.phantom_loader = phantom_loader
        
    async def analyze_with_phantom(
        self, 
        phantom_id: str, 
        market_context: str
    ) -> dict:
        """Single phantom analysis"""
        phantom = self.phantom_loader.get(phantom_id)
        if not phantom:
            raise ValueError(f"Unknown phantom: {phantom_id}")
        
        system_prompt = PhantomPromptBuilder.build_system_prompt(phantom)
        
        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=1.0,  # Higher temperature for distinct responses
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": market_context
            }]
        )
        
        return {
            "phantom_id": phantom_id,
            "phantom_name": phantom.name,
            "analysis": response.content[0].text
        }
    
    async def analyze_with_council(
        self, 
        market_context: str, 
        phantom_ids: list[str] | None = None
    ) -> list[dict]:
        """Run analysis with multiple phantoms in parallel"""
        if phantom_ids is None:
            phantom_ids = self.phantom_loader.list_ids()
        
        # Execute all phantom analyses concurrently
        tasks = [
            self.analyze_with_phantom(pid, market_context) 
            for pid in phantom_ids
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out any failures
        successful_results = [
            r for r in results 
            if not isinstance(r, Exception)
        ]
        
        return successful_results
```

---

### Pattern 4: Market Context Builder

**When:** Formatting market data for phantom consumption

```python
# backend/src/core/market_fetcher.py

class MarketContextBuilder:
    @staticmethod
    def build_context(market_data: dict) -> str:
        """Format market data into natural language context for phantoms"""
        
        symbol = market_data["symbol"]
        price_data = market_data["price"]
        fundamentals = market_data.get("fundamentals", {})
        news = market_data.get("recent_news", [])
        
        context = f"""MARKET ANALYSIS REQUEST: {symbol}

CURRENT SITUATION:
• Price: ${price_data['current']:.2f} ({price_data['change']:+.2f}, {price_data['change_percent']:+.2f}%)
• 52-week range: ${fundamentals.get('week_52_low', 'N/A')} - ${fundamentals.get('week_52_high', 'N/A')}

FUNDAMENTALS:
• P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}
• Market Cap: {fundamentals.get('market_cap', 'N/A')}
• Revenue Growth: {fundamentals.get('revenue_growth', 'N/A')}
• Profit Margin: {fundamentals.get('profit_margin', 'N/A')}

RECENT DEVELOPMENTS:
"""
        
        for item in news[:5]:  # Top 5 news items
            context += f"\n• {item['title']} ({item['source']}, {item['published']})"
        
        context += """

YOUR TASK:
Analyze this opportunity through your investment framework. Provide:
1. Immediate gut reaction (< 20 words)
2. Which of your past experiences this reminds you of
3. Strategic position: BULLISH / BEARISH / NEUTRAL / AVOID
4. Conviction level: 1-10
5. Key opportunities you see
6. Key risks you see
7. What you might be missing due to your blind spots
"""
        
        return context
```

---

### Pattern 5: Response Parsing with Structured Output

**When:** Extracting structured data from phantom analyses

```python
# backend/src/models/forecast.py
from pydantic import BaseModel, Field
from enum import Enum

class Position(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    AVOID = "avoid"

class PhantomForecast(BaseModel):
    phantom_id: str
    phantom_name: str
    gut_reaction: str = Field(..., max_length=200)
    conviction: int = Field(..., ge=1, le=10)
    position: Position
    opportunities: list[str]
    risks: list[str]
    reasoning: str
    reminds_of: str  # Which memory/pattern
    blind_spot_check: str

class ForecastParser:
    """Parse Claude responses into structured forecasts"""
    
    @staticmethod
    def parse_analysis(phantom_id: str, phantom_name: str, raw_text: str) -> PhantomForecast:
        """
        Parse Claude's free-form response into structured forecast.
        
        NOTE: In production, use Claude's structured output API.
        For MVP, use regex/basic parsing.
        """
        # This is simplified - in real implementation:
        # 1. Use Claude's structured output via response_format
        # 2. Or use a second Claude call to structure the output
        # 3. Or implement robust regex parsing
        
        # For now, assume Claude follows format in prompt
        lines = raw_text.split('\n')
        
        # Extract components (simplified)
        gut_reaction = lines[0] if lines else ""
        conviction = 5  # Default, parse from text
        position = Position.NEUTRAL  # Parse from text
        
        return PhantomForecast(
            phantom_id=phantom_id,
            phantom_name=phantom_name,
            gut_reaction=gut_reaction,
            conviction=conviction,
            position=position,
            opportunities=[],
            risks=[],
            reasoning=raw_text,
            reminds_of="",
            blind_spot_check=""
        )
```

---

### Pattern 6: Synthesis Generation

**When:** Combining multiple phantom analyses into unified insights

```python
# backend/src/core/synthesis.py

class SynthesisEngine:
    def __init__(self, anthropic_client: AsyncAnthropic):
        self.client = anthropic_client
    
    async def synthesize(self, phantom_forecasts: list[dict]) -> dict:
        """Generate synthesis across all phantom analyses"""
        
        # Build synthesis context
        analyses_text = "\n\n---\n\n".join([
            f"{f['phantom_name']} Analysis:\n{f['analysis']}"
            for f in phantom_forecasts
        ])
        
        synthesis_prompt = f"""You are analyzing multiple investment perspectives on the same market opportunity.

Below are analyses from {len(phantom_forecasts)} legendary investors, each applying their distinct framework:

{analyses_text}

Your task is to synthesize these competing perspectives and identify:

1. CONSENSUS POINTS: What do these investors agree on? (Even implicit agreement)

2. KEY DISAGREEMENTS: Where do they fundamentally disagree and WHY? 
   - Map disagreements to underlying philosophical differences
   - Example: "Buffett sees value, Burry sees bubble - classic value vs contrarian split"

3. NON-OBVIOUS INSIGHTS: What is NO ONE talking about? What are ALL of them missing?
   - Look for systematic blind spots
   - Identify second-order effects none mentioned

4. SYNTHESIS RECOMMENDATION: Weighing all perspectives, what's the strategic call?
   - Don't just average - identify which framework fits current conditions best
   - Assign confidence level: LOW / MEDIUM / HIGH

Be provocative about disagreements. Don't smooth over conflicts - they're where the insight lives."""

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            temperature=0.7,
            messages=[{"role": "user", "content": synthesis_prompt}]
        )
        
        return {
            "synthesis_text": response.content[0].text,
            "phantom_count": len(phantom_forecasts)
        }
```

---

## API Route Patterns

### Pattern 7: FastAPI Route with Error Handling

**When:** Creating API endpoints

```python
# backend/src/api/routes/phantom.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/phantom", tags=["phantom"])

class AnalysisRequest(BaseModel):
    market_data_id: str
    phantom_ids: list[str] | None = None

@router.post("/analyze")
async def analyze_market(
    request: AnalysisRequest,
    phantom_engine: PhantomEngine = Depends(get_phantom_engine)
) -> dict:
    """Run phantom council analysis on market data"""
    
    try:
        # Fetch market data
        market_data = await get_market_data(request.market_data_id)
        if not market_data:
            raise HTTPException(status_code=404, detail="Market data not found")
        
        # Build context
        context = MarketContextBuilder.build_context(market_data)
        
        # Run phantom analyses
        analyses = await phantom_engine.analyze_with_council(
            market_context=context,
            phantom_ids=request.phantom_ids
        )
        
        return {
            "market_data_id": request.market_data_id,
            "analyses": analyses,
            "count": len(analyses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Frontend Patterns

### Pattern 8: React Server Component Data Fetching

**When:** Loading market data in Next.js

```typescript
// frontend/src/app/(dashboard)/page.tsx
import { PhantomCouncil } from '@/components/phantom/phantom-council'

async function getMarketData(symbol: string) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/market/fetch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol }),
    cache: 'no-store'  // Always fresh market data
  })
  
  if (!res.ok) throw new Error('Failed to fetch market data')
  return res.json()
}

export default async function Dashboard({ searchParams }: { 
  searchParams: { symbol?: string } 
}) {
  const symbol = searchParams.symbol || 'AAPL'
  const marketData = await getMarketData(symbol)
  
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Phantom Council Analysis</h1>
      <PhantomCouncil symbol={symbol} marketDataId={marketData.id} />
    </div>
  )
}
```

---

### Pattern 9: Client Component with Streaming Updates

**When:** Showing real-time phantom analysis progress

```typescript
// frontend/src/components/phantom/phantom-council.tsx
'use client'

import { useState, useEffect } from 'react'
import { PhantomCard } from './phantom-card'

interface PhantomAnalysis {
  phantom_id: string
  phantom_name: string
  analysis: string
  status: 'pending' | 'analyzing' | 'complete'
}

export function PhantomCouncil({ symbol, marketDataId }: { 
  symbol: string
  marketDataId: string 
}) {
  const [analyses, setAnalyses] = useState<PhantomAnalysis[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  async function runAnalysis() {
    setIsLoading(true)
    
    try {
      const response = await fetch('/api/phantom/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ market_data_id: marketDataId })
      })
      
      const data = await response.json()
      setAnalyses(data.analyses.map((a: any) => ({
        ...a,
        status: 'complete'
      })))
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="space-y-6">
      <button 
        onClick={runAnalysis}
        disabled={isLoading}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {isLoading ? 'Analyzing...' : 'Run Phantom Council Analysis'}
      </button>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {analyses.map((analysis) => (
          <PhantomCard key={analysis.phantom_id} analysis={analysis} />
        ))}
      </div>
    </div>
  )
}
```

---

## Database Patterns

### Pattern 10: Supabase Client (Server-Side)

**When:** Querying database from backend

```python
# backend/src/services/supabase_service.py
from supabase import create_client, Client
import os

class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        )
    
    async def save_forecast(self, forecast_data: dict) -> dict:
        """Save phantom forecast to database"""
        result = self.client.table("forecasts").insert(forecast_data).execute()
        return result.data[0] if result.data else None
    
    async def get_market_data(self, market_data_id: str) -> dict | None:
        """Retrieve market data snapshot"""
        result = self.client.table("market_data")\
            .select("*")\
            .eq("id", market_data_id)\
            .single()\
            .execute()
        return result.data
```

---

## Testing Patterns

### Pattern 11: Phantom Test Harness

**When:** Testing phantom consistency

```python
# backend/tests/test_phantom_consistency.py
import pytest
from src.core.phantom_engine import PhantomEngine

@pytest.mark.asyncio
async def test_phantom_maintains_personality(phantom_engine):
    """Test that phantom gives consistent responses to similar situations"""
    
    # Create two similar market scenarios
    scenario_1 = "Tech stock with PE of 50, high growth, no profits"
    scenario_2 = "Software company with PE of 45, strong revenue growth, negative earnings"
    
    # Run Buffett phantom on both
    result_1 = await phantom_engine.analyze_with_phantom("buffett", scenario_1)
    result_2 = await phantom_engine.analyze_with_phantom("buffett", scenario_2)
    
    # Both should be skeptical/avoid due to value framework
    assert "value" in result_1["analysis"].lower()
    assert "value" in result_2["analysis"].lower()
    # Should show consistency in position
    # (parsing logic would extract position from analysis)
```

---

## Error Handling Patterns

### Pattern 12: Graceful Phantom Failure

**When:** One phantom fails but others shouldn't

```python
async def analyze_with_council_safe(
    self, 
    market_context: str, 
    phantom_ids: list[str] | None = None
) -> dict:
    """Run analysis with graceful failure handling"""
    
    if phantom_ids is None:
        phantom_ids = self.phantom_loader.list_ids()
    
    results = []
    errors = []
    
    for phantom_id in phantom_ids:
        try:
            result = await self.analyze_with_phantom(phantom_id, market_context)
            results.append(result)
        except Exception as e:
            errors.append({
                "phantom_id": phantom_id,
                "error": str(e)
            })
            # Log but continue with other phantoms
            logger.error(f"Phantom {phantom_id} failed: {e}")
    
    return {
        "successful_analyses": results,
        "failed_phantoms": errors,
        "success_rate": len(results) / len(phantom_ids)
    }
```
