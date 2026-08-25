"""NLP Service wrapping the trained ML baseline classifier.

Conforms strictly to:
- backend.md: services.nlp_service wraps model predict() logic, validates inputs, handles failures.
- feature-specification.md: FEAT-04 NLP classification track.
- url-analysis-and-risk-engine.md: Fallback internal score 0.50 on model failure.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from models.src.baseline_model import RakshaBaselineClassifier
from models.src.preprocessor import TextPreprocessor, preprocessor

logger = logging.getLogger(__name__)

DEFAULT_MODEL_DIR = REPO_ROOT / "models" / "saved_models" / "baseline_tfidf"


class NLPService:
    """Service managing ML inference and preprocessing for text phishing intent."""

    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = model_dir or DEFAULT_MODEL_DIR
        self.preprocessor = preprocessor
        self.model: Optional[RakshaBaselineClassifier] = None
        self._load_model()

    def _load_model(self) -> None:
        """Loads the serialized baseline classifier if available."""
        try:
            if (self.model_dir / "baseline_model.joblib").exists():
                self.model = RakshaBaselineClassifier.load(self.model_dir)
                logger.info(f"Successfully loaded baseline model from {self.model_dir}")
            else:
                logger.warning(f"Baseline model not found at {self.model_dir}. Operating in degraded mode.")
                self.model = None
        except Exception as e:
            logger.error(f"Failed to load baseline model: {e}")
            self.model = None

    def analyze(self, text: str, has_url: bool = False) -> Dict[str, Any]:
        """Analyzes text for phishing probability and language signals.
        
        Handles model inference failures gracefully with deterministic fallback.
        """
        # Preprocess input text
        prep_res = self.preprocessor.preprocess(text)
        language_detected = prep_res.language
        script_detected = prep_res.script

        # Check if input is URL-only (no alphabetic text besides URLs)
        is_url_only = False
        text_without_urls = " ".join([t for t in prep_res.tokens if not t.startswith("http") and not t.startswith("www")])
        if has_url and not any(c.isalpha() for c in text_without_urls):
            is_url_only = True

        # If model is unavailable or failed, use deterministic fallback
        if self.model is None or not self.model.is_fitted:
            return {
                "nlp_score": 0.0 if is_url_only else 0.50,
                "language_detected": language_detected,
                "script": script_detected,
                "is_degraded": True,
                "is_url_only": is_url_only,
                "indicators": ["Analysis partially degraded."],
            }

        try:
            # If URL-only, nlp_score is 0.0 per url-analysis-and-risk-engine.md#L12
            if is_url_only:
                return {
                    "nlp_score": 0.0,
                    "language_detected": language_detected,
                    "script": script_detected,
                    "is_degraded": False,
                    "is_url_only": True,
                    "indicators": [],
                }

            pred_res = self.model.predict_single(text)
            nlp_score = pred_res["nlp_score"]
            indicators = []
            if nlp_score >= 0.75:
                indicators.append("High phishing intent detected in message text")
            elif nlp_score >= 0.40:
                indicators.append("Suspicious linguistic patterns detected in message")

            return {
                "nlp_score": nlp_score,
                "language_detected": language_detected,
                "script": script_detected,
                "is_degraded": False,
                "is_url_only": False,
                "indicators": indicators,
            }

        except Exception as e:
            logger.error(f"NLP model inference error: {e}")
            return {
                "nlp_score": 0.50,
                "language_detected": language_detected,
                "script": script_detected,
                "is_degraded": True,
                "is_url_only": is_url_only,
                "indicators": ["Analysis partially degraded."],
            }


# Global singleton instance
nlp_service = NLPService()
