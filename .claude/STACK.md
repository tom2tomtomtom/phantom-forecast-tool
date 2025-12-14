# Technology Stack - Phantom Forecast Tool

## Approved Versions

| Technology | Version | Lock Level | Notes |
|------------|---------|------------|-------|
| Node.js | 20.x LTS | Major | Do not use 21+ |
| Next.js | 15.x | Major | App Router only |
| React | 19.x | Major | With Server Components |
| TypeScript | 5.x | Major | Strict mode |
| Tailwind CSS | 3.4.x | Minor | With Prettier plugin |
| Python | 3.11+ | Major | For phantom system backend |
| Anthropic API | Claude Sonnet 4.5 | Major | Primary AI engine |

## Core Architecture Layers

### Frontend Stack
- **Next.js 15** - Web interface
- **React 19** - UI components
- **Tailwind CSS** - Styling
- **Recharts** - Market data visualization
- **shadcn/ui** - Component library base

### Backend Stack
- **Python FastAPI** - Phantom system API
- **Anthropic Claude API** - AI reasoning engine
- **APScheduler** - Automated daily scans (Phase 2)
- **n8n** - Workflow automation (optional integration)
- **Supabase** - Data persistence & auth

### Data Layer
- **Perplexity API** - Real-time market intelligence (PRIMARY)
- **Financial Modeling Prep (FMP)** - Financial data & fundamentals (Phase 2)
- **Alpha Vantage** - Price data alternative (free tier)
- **Yahoo Finance API** - Market data fallback
- **PostgreSQL** - Historical forecast storage
- **Redis** - Real-time data cache (optional)

## Package Lock

### Frontend Dependencies

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@supabase/supabase-js": "^2.45.0",
    "@supabase/ssr": "^0.5.0",
    "recharts": "^2.10.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "date-fns": "^3.0.0",
    "zustand": "^4.5.0"
  }
}
```

### Backend Dependencies (Python)

#### Phase 1 - Core (CURRENT)
```txt
fastapi==0.109.0
uvicorn==0.27.0
anthropic==0.18.0
pydantic==2.6.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.26.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
```

#### Phase 2 - Opportunity Detection (PLANNED)
```txt
# Scheduling
apscheduler==3.10.4         # Daily scan automation

# Financial Data
financialmodelingprep==0.1.0  # FMP API client (or build custom)
alpha-vantage==2.3.1          # Price data alternative
yfinance==0.2.35              # Yahoo Finance (backup)

# Analysis
pandas==2.1.4               # Data manipulation for triggers
numpy==1.26.3               # Statistical analysis

# Caching (Optional)
redis==5.0.0                # Response caching
aioredis==2.0.1             # Async Redis client

# Email (Optional)
sendgrid==6.11.0            # Daily digest emails
python-dotenv==1.0.0        # Already included
```

### Complete Phase 2 requirements.txt
```txt
# Phase 1 (Existing)
fastapi==0.109.0
uvicorn[standard]==0.27.0
anthropic==0.18.0
pydantic==2.6.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.26.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9

# Phase 2 Additions
apscheduler==3.10.4
pandas==2.1.4
numpy==1.26.3
yfinance==0.2.35
redis==5.0.0  # Optional
aioredis==2.0.1  # Optional
sendgrid==6.11.0  # Optional
```

## Phantom System Architecture

### Phantom Definition Format (JSON)

```json
{
  "investor_id": "buffett",
  "name": "Warren Buffett",
  "philosophy": "Value investing, economic moats, long-term compounding",
  "phantom_memories": [
    {
      "context": "Market situation description",
      "decision": "Investment action taken",
      "reasoning": "Strategic logic",
      "outcome": "Result and lesson learned",
      "lesson": "Strategic insight gained"
    }
  ],
  "trigger_patterns": [
    "undervalued assets with strong fundamentals",
    "companies with durable competitive advantages"
  ],
  "blind_spots": [
    "technology sector complexity",
    "short-term market movements"
  ]
}
```

## API Integration Points

### Anthropic Claude Integration

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Phantom reasoning call
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2000,
    temperature=1.0,  # High for distinct phantom voices
    system=phantom_system_prompt,
    messages=[
        {"role": "user", "content": market_data_context}
    ]
)
```

### Market Data Integration (Phase 2)

#### Perplexity - Market Intelligence (PRIMARY)
```python
import httpx

async def fetch_market_intelligence(symbol: str) -> str:
    """Get recent news and sentiment via Perplexity."""
    response = await httpx.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"},
        json={
            "model": "sonar-pro",
            "messages": [{
                "role": "user", 
                "content": f"{symbol} stock recent news earnings risks opportunities"
            }]
        },
        timeout=30.0
    )
    return response.json()
```

#### Financial Modeling Prep - Fundamentals
```python
async def fetch_fundamentals(symbol: str) -> dict:
    """Get valuation metrics and financial data."""
    async with httpx.AsyncClient() as client:
        # Key metrics
        metrics = await client.get(
            f"https://financialmodelingprep.com/api/v3/key-metrics/{symbol}",
            params={"apikey": FMP_API_KEY}
        )
        
        # Valuation ratios
        ratios = await client.get(
            f"https://financialmodelingprep.com/api/v3/ratios/{symbol}",
            params={"apikey": FMP_API_KEY}
        )
        
        return {
            "metrics": metrics.json(),
            "ratios": ratios.json()
        }
```

#### Alpha Vantage - Price Data
```python
async def fetch_price_data(symbol: str) -> dict:
    """Get price action and technical indicators."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": ALPHA_VANTAGE_API_KEY
            }
        )
        return response.json()
```

## Scheduling System (Phase 2)

### APScheduler Configuration

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Daily scan at 8:00 AM ET (before market open)
scheduler = AsyncIOScheduler()
scheduler.add_job(
    run_daily_opportunity_scan,
    trigger=CronTrigger(hour=8, minute=0, timezone="America/New_York"),
    id="daily_opportunity_scan",
    name="Daily Opportunity Detection Scan"
)
scheduler.start()
```

## Adding New Dependencies

Before adding ANY new package:
1. Check if functionality exists in current stack
2. Verify package is actively maintained (last update < 6 months)
3. Check bundle size impact (frontend)
4. Assess API rate limits and costs
5. Document in this file under "Additional Dependencies"

### Approved Additional Dependencies

| Package | Purpose | Added Date | Phase |
|---------|---------|------------|-------|
| `lucide-react` | Icons | Initial | 1 |
| `zod` | Schema validation | Initial | 1 |
| `apscheduler` | Daily scan automation | Phase 2 | 2 |
| `pandas` | Data manipulation | Phase 2 | 2 |
| `numpy` | Statistical analysis | Phase 2 | 2 |
| `yfinance` | Yahoo Finance API | Phase 2 | 2 |

### Explicitly Forbidden

| Package | Reason | Alternative |
|---------|--------|-------------|
| `moment` | Bundle size | `date-fns` |
| `lodash` | Tree-shaking issues | Native JS |
| `axios` | Unnecessary | `httpx` (Python), `fetch` (JS) |
| `openai` | Wrong AI provider | `anthropic` SDK |
| `beautifulsoup4` | Not needed | Direct API integration |
| `scrapy` | Overkill | `httpx` for API calls |

## Environment Variables Required

### Phase 1 (Current)
```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Database
SUPABASE_DATABASE_URL=postgresql://...
# OR for development
DATABASE_URL=sqlite:///./phantom_forecast.db

# Application
ENVIRONMENT=development
DEBUG=true
```

### Phase 2 (Opportunity Detection)
```bash
# Phase 1 variables (above)

# Market Data APIs
PERPLEXITY_API_KEY=pplx-...
FMP_API_KEY=...  # Financial Modeling Prep
ALPHA_VANTAGE_API_KEY=...  # Optional fallback

# Caching (Optional)
REDIS_URL=redis://localhost:6379

# Email Notifications (Optional)
SENDGRID_API_KEY=...
NOTIFICATION_EMAIL=alerts@example.com

# Scheduling
DAILY_SCAN_ENABLED=true
SCAN_TIME_HOUR=8  # 8 AM ET
SCAN_TIME_TIMEZONE=America/New_York

# Application
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## API Rate Limits & Costs

| Service | Free Tier | Paid Tier | Rate Limit | Notes |
|---------|-----------|-----------|------------|-------|
| Anthropic | N/A | Pay-per-use | 4000 req/min | ~$0.003/1K tokens |
| Perplexity | N/A | $20/mo | 600 searches/day | Primary intelligence |
| FMP | 250 req/day | $30/mo | 250-750/day | Financial data |
| Alpha Vantage | 25 req/day | $50/mo | 25-75/day | Price data fallback |
| Yahoo Finance | Free | Free | Unofficial | Backup only |

### Cost Estimation (Phase 2)

**Daily Full Market Scan (~3000 symbols):**
- Trigger detection: ~100 symbols pass filters
- Perplexity: 100 queries × $0.033 = $3.30/day
- FMP: 100 queries (free tier) = $0/day
- Anthropic: 100 council analyses × 6 phantoms = 600 API calls
  - ~600 calls × 2000 tokens × $0.003/1K = $3.60/day
- **Total: ~$7/day = $210/month**

**Watchlist Scan (50 symbols):**
- ~$0.35/day = $10.50/month

**Recommendation:** Start with watchlist, scale to full market if valuable.

## Deployment Stack

| Component | Platform | Notes |
|-----------|----------|-------|
| Frontend | Railway | Next.js deployment |
| Python API | Railway | FastAPI service |
| Database | Supabase | Managed PostgreSQL |
| Cache | Railway Redis | Optional add-on |
| Scheduler | Railway | APScheduler in FastAPI |

## Development Tools

| Tool | Purpose |
|------|---------|
| Cursor | Primary IDE |
| Claude Code | Testing & QA |
| Augment | Large refactoring |
| Supabase Studio | Database management |
| Railway CLI | Deployment management |

## API Client Libraries

### Python (Backend)
```python
# Recommended client structure
class MarketDataService:
    def __init__(self):
        self.perplexity = PerplexityClient(api_key=PERPLEXITY_API_KEY)
        self.fmp = FMPClient(api_key=FMP_API_KEY)
        self.alpha_vantage = AlphaVantageClient(api_key=ALPHA_VANTAGE_API_KEY)
    
    async def enrich_context(self, symbol: str) -> EnrichedContext:
        # Parallel data fetching
        news, fundamentals, price = await asyncio.gather(
            self.perplexity.get_intelligence(symbol),
            self.fmp.get_fundamentals(symbol),
            self.alpha_vantage.get_price(symbol)
        )
        return EnrichedContext(news=news, fundamentals=fundamentals, price=price)
```

### TypeScript (Frontend)
```typescript
// API client for opportunity endpoints
class OpportunityAPI {
  private baseUrl: string;
  
  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }
  
  async quickScan(symbols: string[]): Promise<OpportunityScore[]> {
    const response = await fetch(`${this.baseUrl}/quick-scan`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({symbols})
    });
    return response.json();
  }
  
  async getTopOpportunities(limit = 20): Promise<Opportunity[]> {
    const response = await fetch(`${this.baseUrl}/opportunities/top?limit=${limit}`);
    return response.json();
  }
}
```

## Performance Requirements

| Operation | Target | Measured | Status |
|-----------|--------|----------|--------|
| Single phantom analysis | <5s | TBD | ⏳ |
| Council analysis (6 phantoms) | <15s | TBD | ⏳ |
| Synthesis generation | <3s | TBD | ⏳ |
| Trigger detection (full market) | <5 min | TBD | ⏳ |
| Data enrichment per symbol | <3s | TBD | ⏳ |
| Opportunity scoring | <1s | TBD | ⏳ |
| Daily scan (100 symbols) | <30 min | TBD | ⏳ |

## Technology Decision Log

### Why Perplexity for Market Intelligence?
- **Pro:** Real-time news aggregation + AI synthesis
- **Pro:** Better than manual web scraping
- **Pro:** Returns synthesized narratives, not just data
- **Con:** Cost ($20/month)
- **Decision:** Primary intelligence source, worth the cost

### Why FMP over Yahoo Finance?
- **Pro:** Official API with rate limits
- **Pro:** Comprehensive fundamental data
- **Pro:** Reliable uptime
- **Con:** Cost after free tier
- **Decision:** Use FMP for fundamentals, yfinance as fallback

### Why APScheduler over Cron?
- **Pro:** Python-native, works in Railway
- **Pro:** Programmatic control
- **Pro:** Async support
- **Con:** Requires process to stay running
- **Decision:** APScheduler for flexibility

### Why Redis Optional?
- **Pro:** Fast caching, reduces API calls
- **Con:** Extra complexity and cost
- **Decision:** Start without, add if API costs high

## Version Compatibility Matrix

| Python | FastAPI | Anthropic SDK | Pandas | APScheduler |
|--------|---------|---------------|--------|-------------|
| 3.11 | ✅ 0.109+ | ✅ 0.18+ | ✅ 2.1+ | ✅ 3.10+ |
| 3.12 | ✅ 0.109+ | ✅ 0.18+ | ✅ 2.1+ | ✅ 3.10+ |
| 3.13 | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD |

**Recommendation:** Use Python 3.11 for maximum compatibility.

## Future Technology Considerations

### Phase 3 (Potential Additions)
- **WebSocket** for real-time opportunity alerts
- **Celery** for distributed task queue (if scaling beyond Railway)
- **Prometheus** for metrics and monitoring
- **Grafana** for dashboards
- **Sentry** for error tracking

### Not Planned (Out of Scope)
- Machine learning models (phantom reasoning is LLM-based)
- Custom backtesting engine (use existing tools)
- Mobile app (web-first)
- Blockchain integration (not relevant)
