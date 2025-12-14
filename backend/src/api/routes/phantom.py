"""
Phantom API router - Phantom investor analysis endpoints.

Provides endpoints for:
- Listing available phantoms
- Getting phantom details
- Running single phantom analysis
- Running council (all phantoms) analysis
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Body

from ...models.phantom import (
    PhantomDefinition,
    PhantomSummary,
    PhantomListResponse,
    PhantomAnalysis,
    CouncilAnalysis,
    AnalysisRequest,
    AnalysisResponse,
    CouncilResponse,
    Position,
    Conviction,
)
from ...services.anthropic_service import (
    load_phantom,
    get_available_phantoms,
    analyze_with_phantom as _analyze_with_phantom,
    analyze_with_council as _analyze_with_council,
    synthesize_council,
)

router = APIRouter(prefix="/phantoms", tags=["phantoms"])


@router.get(
    "",
    response_model=PhantomListResponse,
    summary="List all phantoms",
    description="""
    Get a list of all available phantom investor personas.

    Each phantom represents a distinct investment philosophy and strategic lens.
    """,
)
async def list_phantoms() -> PhantomListResponse:
    """List all available phantom personas."""
    phantom_ids = get_available_phantoms()
    phantoms = []

    for pid in phantom_ids:
        phantom = load_phantom(pid)
        if phantom:
            phantoms.append(PhantomSummary(
                investor_id=phantom.investor_id,
                name=phantom.name,
                philosophy=phantom.philosophy,
            ))

    return PhantomListResponse(phantoms=phantoms, total=len(phantoms))


@router.post(
    "/council/analyze",
    response_model=CouncilResponse,
    summary="Analyze with phantom council",
    description="""
    Run analysis on an asset using ALL phantom personas simultaneously.

    This is the core feature - multiple phantoms analyze the same market data
    through their distinct lenses, revealing strategic disagreements and
    non-obvious opportunities.

    Phantoms analyze in parallel for efficiency.
    """,
)
async def analyze_with_council(
    request: AnalysisRequest = Body(...),
) -> CouncilResponse:
    """Analyze an asset with the full phantom council."""
    try:
        # Get phantom IDs to use
        phantom_ids = request.phantom_ids or get_available_phantoms()

        if not phantom_ids:
            raise HTTPException(
                status_code=400,
                detail="No phantoms available for analysis"
            )

        # Run parallel analysis
        analyses = await _analyze_with_council(
            asset=request.asset,
            phantom_ids=phantom_ids,
            context=request.context,
        )

        if not analyses:
            raise HTTPException(
                status_code=500,
                detail="No analyses returned from council"
            )

        # Synthesize the results
        synthesis = await synthesize_council(request.asset, analyses)

        # Determine consensus from synthesis
        consensus_str = synthesis.get("consensus_position")
        consensus = Position(consensus_str) if consensus_str and consensus_str != "null" else None

        # Extract disagreements
        disagreements = []
        for d in synthesis.get("key_disagreements", []):
            if isinstance(d, dict):
                disagreements.append(f"{d.get('topic', 'Unknown')}: {d.get('driver', '')}")
            else:
                disagreements.append(str(d))

        # Add synthesis summary if no structured disagreements
        if not disagreements and synthesis.get("synthesis"):
            disagreements.append(synthesis.get("synthesis"))

        council = CouncilAnalysis(
            asset=request.asset,
            analyses=analyses,
            consensus=consensus,
            disagreements=disagreements,
        )

        return CouncilResponse(success=True, council=council)

    except Exception as e:
        return CouncilResponse(success=False, error=str(e))


@router.get(
    "/{phantom_id}",
    response_model=PhantomSummary,
    summary="Get phantom details",
    description="""
    Get detailed information about a specific phantom investor persona.

    Includes their investment philosophy, trigger patterns, and blind spots.
    """,
)
async def get_phantom(phantom_id: str) -> PhantomSummary:
    """Get details for a specific phantom."""
    phantom = load_phantom(phantom_id)

    if not phantom:
        available = get_available_phantoms()
        raise HTTPException(
            status_code=404,
            detail=f"Phantom '{phantom_id}' not found. Available: {available}"
        )

    return PhantomSummary(
        investor_id=phantom.investor_id,
        name=phantom.name,
        philosophy=phantom.philosophy,
    )


@router.get(
    "/{phantom_id}/full",
    response_model=PhantomDefinition,
    summary="Get full phantom definition",
    description="""
    Get the complete phantom definition including memories, triggers, and blind spots.
    """,
)
async def get_phantom_full(phantom_id: str) -> PhantomDefinition:
    """Get full phantom definition."""
    phantom = load_phantom(phantom_id)

    if not phantom:
        available = get_available_phantoms()
        raise HTTPException(
            status_code=404,
            detail=f"Phantom '{phantom_id}' not found. Available: {available}"
        )

    return phantom


@router.post(
    "/{phantom_id}/analyze",
    response_model=AnalysisResponse,
    summary="Analyze with single phantom",
    description="""
    Run analysis on an asset using a single phantom's perspective.

    The phantom will analyze the asset through its unique strategic lens,
    providing position, conviction, reasoning, and acknowledged blind spots.
    """,
)
async def analyze_with_phantom(
    phantom_id: str,
    asset: str = Query(..., description="Asset to analyze (e.g., 'AAPL', 'BTC')"),
    context: Optional[str] = Query(None, description="Additional market context"),
) -> AnalysisResponse:
    """Analyze an asset with a single phantom."""
    # Verify phantom exists
    phantom = load_phantom(phantom_id)
    if not phantom:
        available = get_available_phantoms()
        raise HTTPException(
            status_code=404,
            detail=f"Phantom '{phantom_id}' not found. Available: {available}"
        )

    try:
        analysis = await _analyze_with_phantom(
            phantom_id=phantom_id,
            asset=asset,
            context=context,
        )
        return AnalysisResponse(success=True, analysis=analysis)

    except Exception as e:
        return AnalysisResponse(success=False, error=str(e))
