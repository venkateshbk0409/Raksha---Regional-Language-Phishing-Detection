"""Deterministic Risk Engine for Raksha.

Conforms strictly to:
- url-analysis-and-risk-engine.md: Pure deterministic math functions,
  Risk_total = (W_nlp * nlp_score) + (W_url * url_score) + Modifiers.
  Weights: W_nlp = 0.60, W_url = 0.40 (with URL), W_nlp = 1.00 (without URL), W_url = 1.00 (URL-only).
  Thresholds: Safe (< 0.40), Suspicious (0.40 - 0.74), Phishing (>= 0.75).
- api-specification.md: ClassificationEnum, LanguageEnum, recommended_action strings.
- backend.md: core.risk_engine pure deterministic scoring.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from backend.app.schemas.analyze import ClassificationEnum, LanguageEnum


@dataclass
class RiskAssessmentResult:
    """Detailed risk assessment outcome containing public and internal signals."""
    classification: ClassificationEnum
    risk_score: float
    language_detected: LanguageEnum
    indicators: List[str]
    recommended_action: str
    nlp_score: float
    url_score: float
    is_degraded: bool = False


class RiskEngine:
    """Deterministic, explainable risk aggregation engine."""

    # Weights defined in url-analysis-and-risk-engine.md
    W_NLP_DEFAULT: float = 0.60
    W_URL_DEFAULT: float = 0.40

    # Thresholds defined in url-analysis-and-risk-engine.md#L53-L55
    SAFE_THRESHOLD: float = 0.40
    PHISHING_THRESHOLD: float = 0.75

    # Standard recommended action strings from api-specification.md
    ACTION_SAFE: str = "No immediate threat detected. Standard vigilance advised."
    ACTION_SUSPICIOUS: str = "Exercise caution. Do not click links or share credentials."
    ACTION_PHISHING: str = "Do not click any links or share sensitive information. Report and delete this message."
    ACTION_DEGRADED: str = "Service experiencing partial degradation. Exercise caution with unverified links."

    @staticmethod
    def map_language(lang_str: str) -> LanguageEnum:
        """Maps internal language string to LanguageEnum."""
        mapping = {
            "kannada": LanguageEnum.KANNADA,
            "english": LanguageEnum.ENGLISH,
            "code-mixed": LanguageEnum.CODE_MIXED,
            "unknown": LanguageEnum.UNKNOWN,
        }
        return mapping.get(lang_str.lower(), LanguageEnum.UNKNOWN)

    def evaluate(
        self,
        nlp_score: float,
        url_score: float,
        has_url: bool,
        url_indicators: Optional[List[str]] = None,
        nlp_indicators: Optional[List[str]] = None,
        language_detected: str = "unknown",
        is_degraded: bool = False,
        is_url_only: bool = False,
    ) -> RiskAssessmentResult:
        """Deterministically calculates final risk score, classification, and indicators.
        
        Formula:
            Risk_total = (W_nlp * nlp_score) + (W_url * url_score) + Modifiers
        """
        # Clamp inputs
        nlp_s = min(1.0, max(0.0, float(nlp_score)))
        url_s = min(1.0, max(0.0, float(url_score)))

        # Determine weights based on input context
        if is_url_only:
            w_nlp = 0.0
            w_url = 1.0
        elif not has_url:
            w_nlp = 1.0
            w_url = 0.0
        else:
            w_nlp = self.W_NLP_DEFAULT
            w_url = self.W_URL_DEFAULT

        # Base weighted calculation
        raw_risk = (w_nlp * nlp_s) + (w_url * url_s)

        # Modifiers
        modifier = 0.0

        # Composite multi-signal threat synergy:
        # When both independent evidence vectors (suspicious message intent + suspicious URL delivery vector)
        # are present, compound the threat score rather than diluting it through a simple arithmetic average.
        if has_url:
            if nlp_s >= 0.45 and url_s >= 0.35:
                modifier += 0.25
            elif nlp_s >= 0.40 and url_s >= 0.45:
                modifier += 0.25
            elif nlp_s >= 0.60 and url_s >= 0.20:
                modifier += 0.15
            elif url_s >= 0.60 and nlp_s >= 0.30:
                modifier += 0.15
            elif url_s >= 0.70:
                modifier += 0.10

        total_risk = raw_risk + modifier

        # Handle degraded mode: minimum floor of 0.50 risk score if degraded
        if is_degraded:
            total_risk = max(0.50, total_risk)

        final_risk_score = round(min(1.0, max(0.0, total_risk)), 4)

        # Determine Classification
        if is_degraded and final_risk_score < self.SAFE_THRESHOLD:
            classification = ClassificationEnum.SUSPICIOUS
        elif final_risk_score >= self.PHISHING_THRESHOLD:
            classification = ClassificationEnum.PHISHING
        elif final_risk_score >= self.SAFE_THRESHOLD:
            classification = ClassificationEnum.SUSPICIOUS
        else:
            classification = ClassificationEnum.SAFE

        # If degraded, force at least SUSPICIOUS
        if is_degraded and classification == ClassificationEnum.SAFE:
            classification = ClassificationEnum.SUSPICIOUS

        # Aggregate unique indicators
        combined_indicators: List[str] = []
        if url_indicators:
            for ind in url_indicators:
                if ind not in combined_indicators:
                    combined_indicators.append(ind)
        if nlp_indicators:
            for ind in nlp_indicators:
                if ind not in combined_indicators:
                    combined_indicators.append(ind)

        # Select Recommended Action
        if is_degraded:
            recommended_action = self.ACTION_DEGRADED
        elif classification == ClassificationEnum.PHISHING:
            recommended_action = self.ACTION_PHISHING
        elif classification == ClassificationEnum.SUSPICIOUS:
            recommended_action = self.ACTION_SUSPICIOUS
        else:
            recommended_action = self.ACTION_SAFE

        return RiskAssessmentResult(
            classification=classification,
            risk_score=final_risk_score,
            language_detected=self.map_language(language_detected),
            indicators=combined_indicators,
            recommended_action=recommended_action,
            nlp_score=nlp_s,
            url_score=url_s,
            is_degraded=is_degraded,
        )


# Global singleton instance
risk_engine = RiskEngine()
