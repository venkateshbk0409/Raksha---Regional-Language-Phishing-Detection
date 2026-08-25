"""Schemas for analysis requests, responses, and error reporting."""

from enum import Enum
from typing import List
from pydantic import BaseModel, Field, field_validator


class ClassificationEnum(str, Enum):
    SAFE = "Safe"
    SUSPICIOUS = "Suspicious"
    PHISHING = "Phishing"


class LanguageEnum(str, Enum):
    KANNADA = "kannada"
    ENGLISH = "english"
    CODE_MIXED = "code-mixed"
    UNKNOWN = "unknown"


class AnalyzeRequest(BaseModel):
    content: str = Field(
        ...,
        description="Text and/or URL content to analyze for phishing (1-2000 characters).",
    )

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content cannot be empty or whitespace-only.")
        return v


class AnalyzeResponse(BaseModel):
    classification: ClassificationEnum
    risk_score: float = Field(..., ge=0.0, le=1.0)
    language_detected: LanguageEnum
    indicators: List[str] = Field(default_factory=list)
    recommended_action: str


class ErrorResponse(BaseModel):
    error_type: str
    message: str
