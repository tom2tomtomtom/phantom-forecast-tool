# CLAUDE.md - Phantom Forecast Tool Project Intelligence

## 🚨 MANDATORY: Read Before ANY Action

Before writing ANY code, you MUST:
1. Read `.claude/STATUS.md` - Know current state
2. Read `.claude/BLUEPRINT.md` - Understand architecture
3. Read `.claude/PATTERNS.md` - Use approved patterns
4. Check relevant task file in `.claude/tasks/`

## Project Identity

**Name:** Phantom Forecast Tool  
**Type:** Experimental AI market intelligence system  
**Purpose:** Test whether phantom memory systems can encode genuine investment judgment  
**Stage:** 📋 Planning → Foundation

## What This Tool Does

This is an experiment to test **pluralistic strategic intelligence** - can we create distinct AI investor personas (phantoms) that analyze markets through fundamentally different lenses?

**Core Hypothesis:** Phantom memory systems can encode strategic judgment (not just stylistic mimicry) that leads to:
- Meaningfully different analyses from same market data
- Strategic disagreements traceable to philosophical frameworks
- Non-obvious insights through synthesis
- Consistent personalities across novel conditions

**NOT a trading system.** This is about testing phantom strategic intelligence quality.

## Tech Stack (Quick Reference)

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | Next.js (App Router) | 15.x |
| Styling | Tailwind CSS | 3.4.x |
| Backend | Python FastAPI | Latest |
| AI Engine | Anthropic Claude | Sonnet 4.5 |
| Database | Supabase (PostgreSQL) | - |
| Market Data | Perplexity API | - |

For complete stack details: `.claude/STACK.md`

## Critical Rules

### NEVER Do Without Checking
- [ ] Create files without checking BLUEPRINT.md for location
- [ ] Add dependencies without checking STACK.md for approved versions
- [ ] Implement features without checking task files for requirements
- [ ] Change patterns without checking PATTERNS.md
- [ ] Use `any` types in TypeScript (strict mode enforced)
- [ ] Store phantoms in database (they're JSON files in version control)

### ALWAYS Do
- [ ] Update STATUS.md after completing any task
- [ ] Follow naming conventions in PATTERNS.md
- [ ] Use approved code patterns - copy, don't invent
- [ ] Mark task checkboxes when complete
- [ ] Handle errors gracefully (one phantom failing shouldn't break others)
- [ ] Use async/await for phantom analyses (they run in parallel)

## Phantom System Special Rules

### Phantom Definitions Are Code, Not Data
- Stored as JSON files in `backend/src/phantoms/*.json`
- Version controlled (Git tracks evolution of strategic judgment)
- Loaded at service startup
- **Do NOT put in database**

### Phantom Memory Format
Each phantom memory must have:
- `context`: Historical market situation
- `decision`: What the phantom did
- `reasoning`: Why (strategic logic)
- `outcome`: What happened
- `lesson`: Strategic insight gained

This is compressed experiential narrative, not marketing copy.

### Temperature Settings
- Phantom analyses: `temperature=1.0` (want distinct responses)
- Synthesis: `temperature=0.7` (want thoughtful but not random)
- Parsing/extraction: `temperature=0.3` (want consistency)

### Parallel Execution Required
Phantoms MUST analyze independently and simultaneously:
```python
# ✅ CORRECT
tasks = [analyze_with_phantom(pid, context) for pid in phantom_ids]
results = await asyncio.gather(*tasks)

# ❌ WRONG - Sequential defeats the purpose
for pid in phantom_ids:
    result = await analyze_with_phantom(pid, context)
```

## Current Focus

**Active Phase:** Phase 1 - Foundation  
**Active Task File:** `.claude/tasks/phase-1-foundation.md`  
**Blockers:** None

## Session Startup Checklist

When starting ANY session:
```
1. Read STATUS.md → Know where we are
2. Read active task file → Know what's next
3. Check DECISIONS.md if architectural questions arise
4. Use PATTERNS.md for all implementations
5. Update STATUS.md after work
```

## Documentation Updates

After completing work:
1. Update STATUS.md with completed items
2. Check off completed tasks in task files
3. Add any new decisions to DECISIONS.md
4. Add any new patterns to PATTERNS.md

## File Location Reference

### Backend Structure
```
backend/src/
├── api/routes/          # API endpoints
├── core/                # Core engines (phantom, market, synthesis)
├── models/              # Pydantic models
├── phantoms/            # Phantom JSON definitions ← Critical
├── services/            # External service integrations
└── tests/               # Test files
```

### Frontend Structure
```
frontend/src/
├── app/                 # Next.js App Router pages
├── components/          # React components
│   ├── ui/             # shadcn base components
│   ├── market/         # Market data displays
│   ├── phantom/        # Phantom persona UI
│   └── synthesis/      # Synthesis views
├── lib/                 # Utilities and API clients
└── types/               # TypeScript type definitions
```

## Key Architectural Decisions

From DECISIONS.md - understand these before coding:

1. **ADR-001:** Phantom system is separate Python service (not Next.js API routes)
2. **ADR-002:** Phantoms are JSON files in Git (not database records)
3. **ADR-003:** Phase 1 = Sequential isolation, Phase 2 = Debate mode
4. **ADR-004:** Real-time analysis prioritized over backtesting
5. **ADR-005:** Perplexity for market intelligence, Alpha Vantage for price
6. **ADR-006:** Synthesis via separate Claude call (not rule-based)
7. **ADR-007:** TypeScript strict mode throughout
8. **ADR-010:** Phantom memories are narrative format (not key-value)

Read full context in `.claude/DECISIONS.md`

## Common Pitfalls to Avoid

### ❌ Don't: Make phantoms too similar
If all phantoms sound the same, the experiment failed. Check their memories - they should have genuinely different formative experiences.

### ❌ Don't: Let synthesis be diplomatic
Synthesis should be provocative about disagreements. That's where insight lives.

### ❌ Don't: Optimize for prediction accuracy
This isn't a trading system. Optimize for strategic disagreement quality.

### ❌ Don't: Add authentication in Phase 1
Per ADR-009, no auth initially. Focus on phantom quality first.

### ❌ Don't: Use OpenAI SDK
Use `anthropic` SDK. This is a Claude-based system.

## Quick Commands

### Check Current State
```bash
cat .claude/STATUS.md | grep "Current Sprint" -A 10
```

### View Active Tasks
```bash
cat .claude/tasks/phase-1-foundation.md | grep "Status:" -B 2 -A 5
```

### List All Decisions
```bash
cat .claude/DECISIONS.md | grep "^## ADR"
```

## Integration with Other Skills

This project uses patterns from:
- **supabase-patterns** - For database operations
- **next-js-app-router** - For frontend routing
- **api-design-patterns** - For FastAPI structure

Reference these when implementing specific features.

## Testing Philosophy

### Phantom Tests Must Verify
- [ ] Distinct responses to same input (not stylistic variation)
- [ ] Philosophical consistency across different scenarios
- [ ] Strategic disagreements traceable to memory differences
- [ ] Blind spot awareness (phantoms acknowledge what they miss)

### Don't Test
- Prediction accuracy (not the goal)
- Response speed (within reason)
- Exact wording (semantic similarity is fine)

## Success Criteria

### Technical Success
- [ ] All phantoms generate analyses in <15 seconds
- [ ] Parallel execution works reliably
- [ ] Database stores forecasts correctly
- [ ] Frontend displays analyses clearly

### Experimental Success
- [ ] Phantoms give meaningfully different analyses
- [ ] Disagreements trace to philosophical differences
- [ ] Synthesis identifies non-obvious insights
- [ ] Phantoms maintain consistency across scenarios

**The experiment succeeds when strategic disagreement is valuable.**

## Emergency Contacts

**Project Owner:** Tom Hyde  
**AI Assistant:** AIDEN  
**Documentation Issues:** Check `.claude/` files first  
**Strategic Questions:** AIDEN can access project knowledge

## Version Info

**Documentation Version:** 0.1.0  
**Last Updated:** 2024-12-13  
**Next Review:** After Phase 1 completion

---

**Remember:** This is an experiment in artificial strategic instinct. The goal isn't perfect forecasts - it's proving phantoms can encode genuine competitive judgment. Stay focused on phantom quality over everything else.
