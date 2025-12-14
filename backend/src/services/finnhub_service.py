"""
Finnhub service for financial market data.

Provides real-time quotes, company profiles, and fundamental metrics.
"""

import asyncio
from typing import Optional
from dataclasses import dataclass

import httpx

from ..config import get_settings

settings = get_settings()

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"


@dataclass
class StockQuote:
    """Real-time stock quote data."""
    symbol: str
    current_price: float
    change: float
    percent_change: float
    high: float
    low: float
    open: float
    previous_close: float
    timestamp: int


@dataclass
class CompanyProfile:
    """Company profile information."""
    symbol: str
    name: str
    market_cap: float
    industry: str
    sector: str
    country: str
    ipo_date: str
    logo: str
    weburl: str


@dataclass
class BasicFinancials:
    """Basic financial metrics."""
    symbol: str
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    ps_ratio: Optional[float]
    dividend_yield: Optional[float]
    beta: Optional[float]
    week_52_high: Optional[float]
    week_52_low: Optional[float]
    week_52_high_date: Optional[str]
    week_52_low_date: Optional[str]
    eps: Optional[float]
    roe: Optional[float]


@dataclass
class FinancialData:
    """Combined financial data for a symbol."""
    quote: Optional[StockQuote]
    profile: Optional[CompanyProfile]
    financials: Optional[BasicFinancials]


async def _finnhub_request(endpoint: str, params: dict = None) -> dict:
    """Make a request to Finnhub API."""
    if not settings.finnhub_api_key:
        raise ValueError("FINNHUB_API_KEY not configured")

    url = f"{FINNHUB_BASE_URL}/{endpoint}"
    params = params or {}
    params["token"] = settings.finnhub_api_key

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)

        if response.status_code == 429:
            # Rate limited - wait and retry once
            await asyncio.sleep(1)
            response = await client.get(url, params=params)

        if response.status_code != 200:
            return {}

        return response.json()


async def get_quote(symbol: str) -> Optional[StockQuote]:
    """Get real-time quote for a symbol."""
    data = await _finnhub_request("quote", {"symbol": symbol.upper()})

    if not data or data.get("c") is None or data.get("c") == 0:
        return None

    return StockQuote(
        symbol=symbol.upper(),
        current_price=data.get("c", 0),
        change=data.get("d", 0),
        percent_change=data.get("dp", 0),
        high=data.get("h", 0),
        low=data.get("l", 0),
        open=data.get("o", 0),
        previous_close=data.get("pc", 0),
        timestamp=data.get("t", 0),
    )


async def get_company_profile(symbol: str) -> Optional[CompanyProfile]:
    """Get company profile for a symbol."""
    data = await _finnhub_request("stock/profile2", {"symbol": symbol.upper()})

    if not data or not data.get("name"):
        return None

    return CompanyProfile(
        symbol=symbol.upper(),
        name=data.get("name", ""),
        market_cap=data.get("marketCapitalization", 0) * 1_000_000,  # Convert to actual value
        industry=data.get("finnhubIndustry", ""),
        sector=data.get("ggroup", ""),
        country=data.get("country", ""),
        ipo_date=data.get("ipo", ""),
        logo=data.get("logo", ""),
        weburl=data.get("weburl", ""),
    )


async def get_basic_financials(symbol: str) -> Optional[BasicFinancials]:
    """Get basic financial metrics for a symbol."""
    data = await _finnhub_request("stock/metric", {"symbol": symbol.upper(), "metric": "all"})

    if not data or not data.get("metric"):
        return None

    metrics = data.get("metric", {})

    return BasicFinancials(
        symbol=symbol.upper(),
        pe_ratio=metrics.get("peBasicExclExtraTTM"),
        pb_ratio=metrics.get("pbQuarterly"),
        ps_ratio=metrics.get("psAnnual"),
        dividend_yield=metrics.get("dividendYieldIndicatedAnnual"),
        beta=metrics.get("beta"),
        week_52_high=metrics.get("52WeekHigh"),
        week_52_low=metrics.get("52WeekLow"),
        week_52_high_date=metrics.get("52WeekHighDate"),
        week_52_low_date=metrics.get("52WeekLowDate"),
        eps=metrics.get("epsBasicExclExtraItemsTTM"),
        roe=metrics.get("roeTTM"),
    )


async def get_financial_data(symbol: str) -> FinancialData:
    """Get all financial data for a symbol in parallel."""
    quote_task = get_quote(symbol)
    profile_task = get_company_profile(symbol)
    financials_task = get_basic_financials(symbol)

    quote, profile, financials = await asyncio.gather(
        quote_task, profile_task, financials_task,
        return_exceptions=True
    )

    return FinancialData(
        quote=quote if isinstance(quote, StockQuote) else None,
        profile=profile if isinstance(profile, CompanyProfile) else None,
        financials=financials if isinstance(financials, BasicFinancials) else None,
    )


async def batch_get_quotes(symbols: list[str]) -> dict[str, StockQuote]:
    """Get quotes for multiple symbols in parallel."""
    tasks = [get_quote(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    quotes = {}
    for symbol, result in zip(symbols, results):
        if isinstance(result, StockQuote):
            quotes[symbol.upper()] = result

    return quotes


def format_financial_context(data: FinancialData) -> str:
    """Format financial data as context string for phantom analysis."""
    parts = []

    if data.quote:
        q = data.quote
        parts.append(f"## Price Data for {q.symbol}")
        parts.append(f"Current: ${q.current_price:.2f} ({q.percent_change:+.2f}%)")
        parts.append(f"Day Range: ${q.low:.2f} - ${q.high:.2f}")
        parts.append(f"Previous Close: ${q.previous_close:.2f}")

    if data.profile:
        p = data.profile
        market_cap_b = p.market_cap / 1_000_000_000
        parts.append(f"\n## Company: {p.name}")
        parts.append(f"Market Cap: ${market_cap_b:.1f}B")
        parts.append(f"Industry: {p.industry}")

    if data.financials:
        f = data.financials
        parts.append(f"\n## Valuation Metrics")
        if f.pe_ratio:
            parts.append(f"P/E Ratio: {f.pe_ratio:.1f}")
        if f.pb_ratio:
            parts.append(f"P/B Ratio: {f.pb_ratio:.2f}")
        if f.dividend_yield:
            parts.append(f"Dividend Yield: {f.dividend_yield:.2f}%")
        if f.week_52_high and f.week_52_low:
            parts.append(f"52-Week Range: ${f.week_52_low:.2f} - ${f.week_52_high:.2f}")
            if data.quote:
                pct_from_high = ((data.quote.current_price - f.week_52_high) / f.week_52_high) * 100
                parts.append(f"Distance from 52W High: {pct_from_high:.1f}%")
        if f.beta:
            parts.append(f"Beta: {f.beta:.2f}")

    return "\n".join(parts) if parts else ""
