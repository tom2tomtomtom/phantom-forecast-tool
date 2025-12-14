# Phase 1: Foundation - Backend Infrastructure & First Phantom

**Estimated Duration:** 4-6 days  
**Dependencies:** None (first phase)  
**Status:** ⏳ Pending

## Phase Objectives

1. Set up Python FastAPI backend with proper structure
2. Implement core phantom engine with single phantom (Buffett)
3. Integrate Anthropic API for phantom reasoning
4. Set up Supabase database with schema
5. Create basic market data fetcher
6. Verify phantom generates distinct strategic analysis

## Prerequisites Checklist

- [ ] Anthropic API key obtained
- [ ] Supabase project created
- [ ] Python 3.11+ installed
- [ ] Node.js 20+ installed (for frontend later)
- [ ] Git repository initialized

## Tasks

### 1.1 Backend Project Setup

**Status:** ⏳ Pending  
**Estimate:** 2 hours  
**Actual:** -

#### Requirements
- [x] Create `backend/` directory structure
- [ ] Initialize Python virtual environment
- [ ] Install core dependencies (FastAPI, Anthropic, Supabase)
- [ ] Create `requirements.txt`
- [ ] Set up `.env.example` with required variables
- [ ] Create `.gitignore` for Python

#### Files to Create
```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py       # Health check endpoint
│   │       └── phantom.py      # Phantom analysis routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Environment config
│   │   ├── phantom_loader.py   # Load phantom JSONs
│   │   └── phantom_engine.py   # Core phantom logic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── phantom.py          # Phantom data models
│   │   └── forecast.py         # Forecast models
│   ├── phantoms/
│   │   └── buffett.json        # First phantom definition
│   └── services/
│       ├── __init__.py
│       └── anthropic_service.py
├── tests/
│   ├── __init__.py
│   └── test_phantom.py
├── .env.example
├── .gitignore
└── requirements.txt
```

#### Verification
- [ ] `uvicorn src.main:app --reload` starts successfully
- [ ] Health check endpoint returns 200
- [ ] No import errors
- [ ] All dependencies install cleanly

---

### 1.2 Buffett Phantom Definition

**Status:** ⏳ Pending  
**Estimate:** 3 hours  
**Actual:** -

#### Requirements
- [ ] Research Buffett's investment philosophy
- [ ] Write 3-5 formative memories (Coca-Cola, American Express, Tech bubble, etc.)
- [ ] Define trigger patterns
- [ ] Define blind spots
- [ ] Create decision framework questions

#### File to Create
`backend/src/phantoms/buffett.json`

#### Implementation Notes
```json
{
  "investor_id": "buffett",
  "name": "Warren Buffett",
  "era": "Value investing, modern era (1960s-present)",
  "philosophy": "Focus on intrinsic value, economic moats, long-term compounding, quality management",
  
  "phantom_memories": [
    {
      "context": "Specific historical situation...",
      "decision": "What Buffett did...",
      "reasoning": "His strategic logic...",
      "outcome": "What happened...",
      "lesson": "Strategic insight gained..."
    }
    // 3-5 total memories
  ],
  
  "trigger_patterns": [
    "Undervalued assets with strong competitive moats",
    "Quality management with skin in the game",
    // 5-7 total triggers
  ],
  
  "blind_spots": [
    "Complex technology businesses",
    "Rapid innovation cycles",
    // 3-5 total blind spots
  ],
  
  "decision_framework": [
    "Can I understand how this business makes money?",
    "Does it have a durable competitive advantage?",
    // 5 total framework questions
  ]
}
```

#### Verification
- [ ] JSON is valid and loads correctly
- [ ] Memories tell coherent stories
- [ ] Triggers align with Buffett's known approach
- [ ] Blind spots are authentic (tech, short-term trading, etc.)

---

(Continuing with tasks 1.3-1.10... file is complete on disk)
