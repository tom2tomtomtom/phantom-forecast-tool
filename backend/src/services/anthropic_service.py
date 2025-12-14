"""
Anthropic Claude service for Phantom reasoning.

This service handles all interactions with the Claude API for:
- Individual phantom analysis
- Council (multi-phantom) analysis
- Synthesis of competing perspectives
"""

import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

import anthropic

from ..config import get_settings
from ..models.phantom import (
    PhantomDefinition,
    PhantomMemory,
    PhantomAnalysis,
    Position,
    Conviction,
)

settings = get_settings()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

# Phantom definitions cache
_phantom_cache: Dict[str, PhantomDefinition] = {}


def load_phantom(phantom_id: str) -> Optional[PhantomDefinition]:
    """
    Load a phantom definition from JSON file.

    Phantoms are stored in backend/src/phantoms/{phantom_id}.json
    """
    if phantom_id in _phantom_cache:
        return _phantom_cache[phantom_id]

    phantom_path = Path(__file__).parent.parent / "phantoms" / f"{phantom_id}.json"

    if not phantom_path.exists():
        return None

    with open(phantom_path, "r") as f:
        data = json.load(f)

    # Convert memories to PhantomMemory objects
    memories = [PhantomMemory(**m) for m in data.get("phantom_memories", [])]

    phantom = PhantomDefinition(
        investor_id=data["investor_id"],
        name=data["name"],
        era=data.get("era", ""),
        philosophy=data["philosophy"],
        phantom_memories=memories,
        trigger_patterns=data.get("trigger_patterns", []),
        blind_spots=data.get("blind_spots", []),
        decision_framework=data.get("decision_framework", []),
    )

    _phantom_cache[phantom_id] = phantom
    return phantom


def build_phantom_system_prompt(phantom: PhantomDefinition) -> str:
    """
    Build the system prompt that establishes the phantom's identity.

    This is the core of phantom reasoning - the compressed experiential narrative
    that shapes how the phantom interprets market signals.
    """
    memories_text = "\n\n".join([
        f"**Memory: {m.context}**\n"
        f"Decision: {m.decision}\n"
        f"Reasoning: {m.reasoning}\n"
        f"Outcome: {m.outcome}\n"
        f"Lesson: {m.lesson}"
        for m in phantom.phantom_memories
    ])

    triggers_text = "\n".join([f"- {t}" for t in phantom.trigger_patterns])
    blind_spots_text = "\n".join([f"- {b}" for b in phantom.blind_spots])
    framework_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(phantom.decision_framework)])

    return f"""You are {phantom.name}, analyzing markets through your distinct investment philosophy.

## Your Investment Philosophy
{phantom.philosophy}

## Your Era and Context
{phantom.era}

## Formative Experiences That Shape Your Judgment
These memories define how you interpret market signals:

{memories_text}

## What Triggers Your Interest
{triggers_text}

## Your Known Blind Spots
Be honest about these limitations in your analysis:
{blind_spots_text}

## Your Decision Framework
Questions you always ask:
{framework_text}

## Analysis Guidelines
1. Analyze through YOUR lens - not a generic analyst's view
2. Reference your past experiences when relevant
3. Acknowledge your blind spots honestly
4. Be specific about conviction level and reasoning
5. If this situation triggers patterns from your memory, explain the connection
6. Disagree with conventional wisdom when your philosophy demands it

You are NOT trying to be balanced or diplomatic. You are {phantom.name}, with strong convictions shaped by decades of experience."""


def build_analysis_prompt(asset: str, context: Optional[str] = None) -> str:
    """Build the user prompt requesting analysis."""
    context_section = f"\n\nAdditional Context:\n{context}" if context else ""

    return f"""Analyze {asset} from your perspective.{context_section}

Provide your analysis in the following JSON format:
{{
    "position": "bullish" | "bearish" | "neutral" | "avoid",
    "conviction": "high" | "medium" | "low",
    "reasoning": "Your strategic reasoning (2-4 sentences explaining WHY based on your philosophy)",
    "key_factors": ["Factor 1", "Factor 2", "Factor 3"],
    "risks": ["Risk 1", "Risk 2"],
    "blind_spots_acknowledged": ["Blind spot that might affect this analysis"]
}}

Be authentic to your investment philosophy. If you would pass on this opportunity, say so clearly."""


async def analyze_with_phantom(
    phantom_id: str,
    asset: str,
    context: Optional[str] = None,
) -> PhantomAnalysis:
    """
    Run analysis using a single phantom's perspective.

    This is the core phantom reasoning function - it establishes the phantom's
    identity through the system prompt and gets their authentic analysis.
    """
    phantom = load_phantom(phantom_id)

    if not phantom:
        # Return error analysis if phantom not found
        raise ValueError(f"Phantom '{phantom_id}' not found")

    system_prompt = build_phantom_system_prompt(phantom)
    user_prompt = build_analysis_prompt(asset, context)

    # Call Claude with high temperature for distinct responses
    response = await asyncio.to_thread(
        client.messages.create,
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=settings.phantom_temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Parse the response
    response_text = response.content[0].text

    # Extract JSON from response (handle markdown code blocks)
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        # If JSON parsing fails, create a fallback analysis
        return PhantomAnalysis(
            phantom_id=phantom_id,
            phantom_name=phantom.name,
            position=Position.NEUTRAL,
            conviction=Conviction.LOW,
            reasoning=f"Analysis parsing error. Raw response: {response_text[:200]}",
            key_factors=["Unable to parse structured response"],
            risks=["Analysis may be incomplete"],
            blind_spots_acknowledged=[],
        )

    return PhantomAnalysis(
        phantom_id=phantom_id,
        phantom_name=phantom.name,
        position=Position(data.get("position", "neutral")),
        conviction=Conviction(data.get("conviction", "medium")),
        reasoning=data.get("reasoning", ""),
        key_factors=data.get("key_factors", []),
        risks=data.get("risks", []),
        blind_spots_acknowledged=data.get("blind_spots_acknowledged", []),
    )


async def analyze_with_council(
    asset: str,
    phantom_ids: Optional[List[str]] = None,
    context: Optional[str] = None,
) -> List[PhantomAnalysis]:
    """
    Run analysis using multiple phantoms in parallel.

    This is the core feature - getting competing perspectives simultaneously.
    Phantoms MUST analyze independently to avoid groupthink.
    """
    # Default to all available phantoms
    if not phantom_ids:
        phantoms_dir = Path(__file__).parent.parent / "phantoms"
        if phantoms_dir.exists():
            phantom_ids = [p.stem for p in phantoms_dir.glob("*.json")]
        else:
            phantom_ids = []

    if not phantom_ids:
        return []

    # Run all phantom analyses in parallel
    tasks = [
        analyze_with_phantom(pid, asset, context)
        for pid in phantom_ids
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions and return successful analyses
    analyses = []
    for result in results:
        if isinstance(result, PhantomAnalysis):
            analyses.append(result)
        elif isinstance(result, Exception):
            # Log error but continue with other phantoms
            print(f"Phantom analysis error: {result}")

    return analyses


async def synthesize_council(
    asset: str,
    analyses: List[PhantomAnalysis],
) -> Dict[str, Any]:
    """
    Synthesize competing phantom perspectives into insights.

    This is NOT about finding consensus - it's about identifying:
    - Where phantoms agree (and why that's significant)
    - Where they disagree (and what drives the disagreement)
    - Non-obvious opportunities revealed by the disagreement
    - Systemic blind spots across the council
    """
    if not analyses:
        return {
            "consensus": None,
            "disagreements": [],
            "synthesis": "No analyses to synthesize",
            "opportunities": [],
            "collective_blind_spots": [],
        }

    # Build synthesis prompt
    analyses_text = "\n\n".join([
        f"## {a.phantom_name} ({a.position.value}, {a.conviction.value} conviction)\n"
        f"Reasoning: {a.reasoning}\n"
        f"Key Factors: {', '.join(a.key_factors)}\n"
        f"Risks: {', '.join(a.risks)}\n"
        f"Acknowledged Blind Spots: {', '.join(a.blind_spots_acknowledged)}"
        for a in analyses
    ])

    synthesis_prompt = f"""You are analyzing competing investment perspectives on {asset}.

Here are the analyses from different investor personas:

{analyses_text}

Synthesize these perspectives. Focus on:
1. DISAGREEMENTS - Where do they differ and WHY? What philosophical differences drive this?
2. CONSENSUS - Where do they agree? Is this meaningful or just conventional wisdom?
3. OPPORTUNITIES - What non-obvious insights emerge from the disagreement?
4. BLIND SPOTS - What are ALL of them missing?

Respond in JSON format:
{{
    "consensus_position": "bullish" | "bearish" | "neutral" | null,
    "consensus_strength": "strong" | "weak" | "none",
    "key_disagreements": [
        {{"topic": "...", "positions": {{"phantom_name": "view"}}, "driver": "philosophical reason for disagreement"}}
    ],
    "synthesis": "2-3 sentence synthesis of the strategic situation",
    "opportunities": ["Non-obvious opportunity 1", "..."],
    "collective_blind_spots": ["What they're all missing"]
}}

Be provocative about disagreements - that's where insight lives."""

    response = await asyncio.to_thread(
        client.messages.create,
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=settings.synthesis_temperature,
        messages=[{"role": "user", "content": synthesis_prompt}],
    )

    response_text = response.content[0].text

    # Extract JSON
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {
            "consensus": None,
            "disagreements": [],
            "synthesis": response_text[:500],
            "opportunities": [],
            "collective_blind_spots": [],
        }


def get_available_phantoms() -> List[str]:
    """Get list of available phantom IDs."""
    phantoms_dir = Path(__file__).parent.parent / "phantoms"
    if not phantoms_dir.exists():
        return []
    return [p.stem for p in phantoms_dir.glob("*.json")]
