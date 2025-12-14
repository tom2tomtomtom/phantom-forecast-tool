# Phantom Forecast Tool - System Blueprint

## System Overview

The Phantom Forecast Tool is a market intelligence platform that combines real-time market data with AI-driven strategic analysis through distinct investor "phantoms" - compressed strategic personalities that embody different investment philosophies (Buffett, Dalio, Burry, Ackman, etc.). Rather than providing a single forecast, the system generates competing strategic perspectives on the same market conditions, creating value through **strategic disagreement** and synthesis.

This is an experimental tool designed to test whether phantom memory systems can encode genuine investment judgment - not just stylistic mimicry, but fundamentally different ways of interpreting identical market signals based on compressed experiential narratives.

Core value: **Pluralistic strategic intelligence** - seeing markets through multiple competing lenses simultaneously.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Next.js Frontend (React 19)                   │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐           │  │
│  │  │  Market    │  │  Phantom   │  │  Synthesis │           │  │
│  │  │  Dashboard │  │  Council   │  │  View      │           │  │
│  │  └────────────┘  └────────────┘  └────────────┘           │  │
│  └────────────────────────┬──────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────┐
│                     API GATEWAY                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              FastAPI Backend (Python)                    │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │   Market     │  │   Phantom    │  │  Synthesis   │   │    │
│  │  │   Fetcher    │  │   Engine     │  │  Engine      │   │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │    │
│  └─────────┼──────────────────┼──────────────────┼───────────┘    │
└────────────┼──────────────────┼──────────────────┼────────────────┘
             │                  │                  │
   ┌─────────┴─────────┬────────┴────────┬─────────┴────────┐
   │                   │                 │                  │
┌──▼──────────┐  ┌─────▼─────────┐ ┌────▼──────────┐ ┌─────▼──────┐
│  Perplexity │  │   Anthropic   │ │   Supabase    │ │   Redis    │
│     API     │  │  Claude API   │ │   Database    │ │   Cache    │
│  (Market    │  │  (Phantom     │ │  (Historical  │ │ (Optional) │
│   Data)     │  │  Reasoning)   │ │   Forecasts)  │ │            │
└─────────────┘  └───────────────┘ └───────────────┘ └────────────┘
```

## System Flow

```
1. User selects market/asset → 
2. Market Fetcher retrieves real-time data → 
3. Data distributed to all Phantom personas → 
4. Each Phantom analyzes through its lens → 
5. Phantoms engage in strategic debate → 
6. Synthesis Engine identifies:
   - Points of consensus
   - Strategic disagreements
   - Non-obvious opportunities
   - Systemic blind spots
→ 7. Results presented with competing perspectives
```

## Directory Structure

```
phantom-forecast-tool/
├── frontend/                       # Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── (dashboard)/       # Main dashboard
│   │   │   │   ├── page.tsx       # Market overview
│   │   │   │   ├── council/       # Phantom council view
│   │   │   │   └── synthesis/     # Synthesis results
│   │   │   └── api/               # API routes (proxy)
│   │   ├── components/
│   │   │   ├── ui/                # shadcn components
│   │   │   ├── market/            # Market data displays
│   │   │   ├── phantom/           # Phantom persona UI
│   │   │   └── synthesis/         # Synthesis views
│   │   ├── lib/
│   │   │   ├── api/               # Backend API client
│   │   │   ├── utils/             # Utilities
│   │   │   └── hooks/             # Custom hooks
│   │   └── types/                 # TypeScript types
│   └── public/
│       └── phantoms/              # Phantom avatar images
│
├── backend/                       # Python FastAPI
│   ├── src/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── market.py      # Market data endpoints
│   │   │   │   ├── phantom.py     # Phantom analysis
│   │   │   │   └── synthesis.py   # Synthesis endpoints
│   │   │   └── middleware/
│   │   ├── core/
│   │   │   ├── config.py          # Configuration
│   │   │   ├── market_fetcher.py  # Market data integration
│   │   │   ├── phantom_engine.py  # Phantom reasoning
│   │   │   └── synthesis.py       # Synthesis logic
│   │   ├── models/
│   │   │   ├── phantom.py         # Phantom data models
│   │   │   ├── market.py          # Market data models
│   │   │   └── forecast.py        # Forecast models
│   │   ├── phantoms/
│   │   │   ├── buffett.json       # Warren Buffett phantom
│   │   │   ├── dalio.json         # Ray Dalio phantom
│   │   │   ├── burry.json         # Michael Burry phantom
│   │   │   ├── ackman.json        # Bill Ackman phantom
│   │   │   ├── munger.json        # Charlie Munger phantom
│   │   │   └── lynch.json         # Peter Lynch phantom
│   │   └── services/
│   │       ├── anthropic_service.py
│   │       ├── perplexity_service.py
│   │       └── supabase_service.py
│   ├── tests/
│   └── requirements.txt
│
├── .claude/                       # Project intelligence
│   ├── BLUEPRINT.md              # This file
│   ├── STATUS.md                 # Progress tracking
│   ├── DECISIONS.md              # Architecture decisions
│   ├── PATTERNS.md               # Code patterns
│   ├── STACK.md                  # Tech stack
│   └── tasks/
│       ├── phase-1-foundation.md
│       ├── phase-2-phantoms.md
│       └── phase-3-synthesis.md
│
└── CLAUDE.md                     # Gatekeeper file
```

(Continuing in next message due to length...)
