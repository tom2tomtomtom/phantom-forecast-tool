"""
Perplexity service for market intelligence.

Uses Perplexity's sonar model to fetch real-time news and context for stock analysis.
"""

import asyncio
from typing import Optional, List
from dataclasses import dataclass

import httpx

from ..config import get_settings

settings = get_settings()

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


@dataclass
class MarketContext:
    """Structured market context for phantom analysis."""
    symbol: str
    summary: str
    key_events: List[str]
    sentiment: str
    recent_price_action: str
    risks: List[str]
    catalysts: List[str]


async def fetch_market_context(
    symbol: str,
    include_news: bool = True,
    include_financials: bool = True,
) -> MarketContext:
    """
    Fetch real-time market context for a symbol using Perplexity.

    Uses the sonar model for web-grounded responses with citations.
    """
    # Build the query based on what we want
    query_parts = [f"{symbol} stock"]

    if include_news:
        query_parts.append("latest news developments earnings")
    if include_financials:
        query_parts.append("valuation metrics price target analyst ratings")

    query_parts.append("risks opportunities catalysts")

    query = " ".join(query_parts)

    prompt = f"""Analyze {symbol} stock with current market context.

Provide a structured analysis including:
1. **Summary**: 2-3 sentence overview of current situation
2. **Key Events**: Recent news and developments (last 30 days)
3. **Sentiment**: Overall market sentiment (bullish/bearish/mixed)
4. **Price Action**: Recent price movement and technical context
5. **Risks**: Key risk factors to watch
6. **Catalysts**: Upcoming events that could move the stock

Focus on facts and recent developments. Be concise but comprehensive."""

    headers = {
        "Authorization": f"Bearer {settings.perplexity_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a financial research assistant. Provide factual, well-sourced market analysis. Be concise and focus on actionable information."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,  # Low temperature for factual responses
        "max_tokens": 1024,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            PERPLEXITY_API_URL,
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            # Return minimal context on error
            return MarketContext(
                symbol=symbol,
                summary=f"Unable to fetch market context for {symbol}. Error: {response.status_code}",
                key_events=[],
                sentiment="unknown",
                recent_price_action="",
                risks=[],
                catalysts=[],
            )

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Parse the structured response
        return _parse_market_context(symbol, content)


def _parse_market_context(symbol: str, content: str) -> MarketContext:
    """Parse Perplexity response into structured MarketContext."""
    # Extract sections from the response
    lines = content.split("\n")

    summary = ""
    key_events = []
    sentiment = "mixed"
    price_action = ""
    risks = []
    catalysts = []

    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        lower_line = line.lower()

        # Detect section headers
        if "summary" in lower_line and ("**" in line or ":" in line):
            current_section = "summary"
            # Try to extract inline summary
            if ":" in line:
                summary = line.split(":", 1)[1].strip().strip("*")
            continue
        elif "key event" in lower_line or "recent" in lower_line and "news" in lower_line:
            current_section = "events"
            continue
        elif "sentiment" in lower_line:
            current_section = "sentiment"
            if ":" in line:
                sent_text = line.split(":", 1)[1].strip().lower()
                if "bullish" in sent_text:
                    sentiment = "bullish"
                elif "bearish" in sent_text:
                    sentiment = "bearish"
                else:
                    sentiment = "mixed"
            continue
        elif "price" in lower_line and ("action" in lower_line or "movement" in lower_line):
            current_section = "price"
            if ":" in line:
                price_action = line.split(":", 1)[1].strip().strip("*")
            continue
        elif "risk" in lower_line:
            current_section = "risks"
            continue
        elif "catalyst" in lower_line:
            current_section = "catalysts"
            continue

        # Add content to appropriate section
        if current_section == "summary" and not summary:
            summary = line.strip("*- ")
        elif current_section == "events" and line.startswith(("-", "*", "•")) or line[0].isdigit():
            key_events.append(line.strip("*-•0123456789. "))
        elif current_section == "price" and not price_action:
            price_action = line.strip("*- ")
        elif current_section == "risks" and (line.startswith(("-", "*", "•")) or line[0].isdigit()):
            risks.append(line.strip("*-•0123456789. "))
        elif current_section == "catalysts" and (line.startswith(("-", "*", "•")) or line[0].isdigit()):
            catalysts.append(line.strip("*-•0123456789. "))

    # If parsing failed, use the whole content as summary
    if not summary:
        summary = content[:500] if len(content) > 500 else content

    return MarketContext(
        symbol=symbol,
        summary=summary,
        key_events=key_events[:5],  # Limit to 5 events
        sentiment=sentiment,
        recent_price_action=price_action,
        risks=risks[:5],  # Limit to 5 risks
        catalysts=catalysts[:5],  # Limit to 5 catalysts
    )


async def batch_fetch_context(symbols: List[str]) -> List[MarketContext]:
    """Fetch market context for multiple symbols in parallel."""
    tasks = [fetch_market_context(symbol) for symbol in symbols]
    return await asyncio.gather(*tasks)


def format_context_for_phantom(context: MarketContext) -> str:
    """Format market context as a string for phantom analysis."""
    parts = [
        f"## Current Market Context for {context.symbol}",
        f"\n**Summary:** {context.summary}",
    ]

    if context.key_events:
        parts.append("\n**Recent Developments:**")
        for event in context.key_events:
            parts.append(f"- {event}")

    parts.append(f"\n**Market Sentiment:** {context.sentiment}")

    if context.recent_price_action:
        parts.append(f"\n**Price Action:** {context.recent_price_action}")

    if context.risks:
        parts.append("\n**Key Risks:**")
        for risk in context.risks:
            parts.append(f"- {risk}")

    if context.catalysts:
        parts.append("\n**Upcoming Catalysts:**")
        for catalyst in context.catalysts:
            parts.append(f"- {catalyst}")

    return "\n".join(parts)
