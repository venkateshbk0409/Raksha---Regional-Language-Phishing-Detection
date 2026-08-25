"""Router for phishing analysis endpoint POST /api/v1/analyze."""

from fastapi import APIRouter, HTTPException, Request, status
from backend.app.schemas.analyze import (
    AnalyzeRequest,
    AnalyzeResponse,
    ClassificationEnum,
    ErrorResponse,
    LanguageEnum,
)

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request / Oversized Payload"},
        422: {"model": ErrorResponse, "description": "Validation Error / Empty Input"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def analyze_content(request: Request, payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze input text/URL for phishing indicators.

    Contract-enforcing endpoint following api-specification.md.
    """
    raw_content = payload.content

    # Strict length check: > 2000 characters must return HTTP 400 per api-specification.md
    if len(raw_content) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input content exceeds the maximum allowed length of 2000 characters.",
        )

    # Basic contract stub for TSK-01
    # Full ML pipeline (TSK-04), URL analysis (TSK-05), and Risk Engine (TSK-06) integrate here.
    return AnalyzeResponse(
        classification=ClassificationEnum.SAFE,
        risk_score=0.0,
        language_detected=LanguageEnum.ENGLISH,
        indicators=[],
        recommended_action="No action required.",
    )
