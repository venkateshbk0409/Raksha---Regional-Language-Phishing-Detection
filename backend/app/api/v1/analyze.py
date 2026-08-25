"""Router for phishing analysis endpoint POST /api/v1/analyze."""

import time
from fastapi import APIRouter, HTTPException, Request, status
from backend.app.core.risk_engine import risk_engine
from backend.app.schemas.analyze import (
    AnalyzeRequest,
    AnalyzeResponse,
    ClassificationEnum,
    ErrorResponse,
    LanguageEnum,
)
from backend.app.services.nlp_service import nlp_service
from backend.app.services.telemetry_service import telemetry_service
from backend.app.services.url_service import url_parser

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

    Contract-enforcing endpoint following api-specification.md, wired to Risk Engine
    and Privacy-Safe Telemetry Service.
    """
    t_start = time.perf_counter()
    raw_content = payload.content

    # Strict length check: > 2000 characters must return HTTP 400 per api-specification.md
    if len(raw_content) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input content exceeds the maximum allowed length of 2000 characters.",
        )

    # 1. Local lexical URL analysis
    url_res = url_parser.analyze(raw_content)

    # 2. NLP phishing classification
    nlp_res = nlp_service.analyze(raw_content, has_url=url_res.has_url)

    # 3. Deterministic risk aggregation
    assessment = risk_engine.evaluate(
        nlp_score=nlp_res["nlp_score"],
        url_score=url_res.url_score,
        has_url=url_res.has_url,
        url_indicators=url_res.indicators,
        nlp_indicators=nlp_res["indicators"],
        language_detected=nlp_res["language_detected"],
        is_degraded=nlp_res["is_degraded"],
        is_url_only=nlp_res["is_url_only"],
    )

    t_end = time.perf_counter()
    latency_ms = int(round((t_end - t_start) * 1000))

    # 4. Privacy-safe telemetry logging (database.md - no raw text/URLs/PII)
    telemetry_service.record_telemetry(
        language_detected=assessment.language_detected,
        has_url=url_res.has_url,
        final_classification=assessment.classification,
        latency_ms=latency_ms,
    )

    return AnalyzeResponse(
        classification=assessment.classification,
        risk_score=assessment.risk_score,
        language_detected=assessment.language_detected,
        indicators=assessment.indicators,
        recommended_action=assessment.recommended_action,
    )
