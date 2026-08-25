"""Comprehensive tests for Risk Engine and Wired /analyze Endpoint (TSK-06).

Verifies compliance with:
- url-analysis-and-risk-engine.md: Deterministic risk scoring, weights, thresholds, indicators.
- api-specification.md: 5-field public contract, HTTP status codes, degraded response.
- backend.md: Lifespan/services architecture, failure handling.
- security.md: SSRF offline safety, payload bounds.
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from backend.app.core.risk_engine import RiskEngine, risk_engine
from backend.app.main import app
from backend.app.schemas.analyze import ClassificationEnum, LanguageEnum
from backend.app.services.nlp_service import NLPService

client = TestClient(app)


def test_deterministic_risk_calculation():
    """Verify identical inputs always yield identical risk calculations."""
    res1 = risk_engine.evaluate(
        nlp_score=0.85,
        url_score=0.70,
        has_url=True,
        url_indicators=["IP address used instead of domain name"],
        nlp_indicators=["High phishing intent detected in message text"],
        language_detected="kannada",
    )
    res2 = risk_engine.evaluate(
        nlp_score=0.85,
        url_score=0.70,
        has_url=True,
        url_indicators=["IP address used instead of domain name"],
        nlp_indicators=["High phishing intent detected in message text"],
        language_detected="kannada",
    )

    assert res1.risk_score == res2.risk_score
    assert res1.classification == res2.classification
    assert res1.indicators == res2.indicators
    assert res1.recommended_action == res2.recommended_action
    assert res1.language_detected == res2.language_detected


def test_clearly_benign_message_via_api():
    """Verify clearly legitimate message returns Safe classification and low risk score."""
    response = client.post(
        "/api/v1/analyze",
        json={"content": "Dear team, our quarterly performance review meeting is scheduled for tomorrow at 10 AM."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Safe"
    assert data["risk_score"] < 0.40
    assert data["language_detected"] == "english"
    assert "No immediate threat" in data["recommended_action"]


def test_clearly_phishing_message_via_api():
    """Verify high-threat message with phishing URL returns Phishing classification."""
    response = client.post(
        "/api/v1/analyze",
        json={"content": "URGENT: Your SBI account has been locked. Verify KYC immediately at http://192.168.1.1/sbi-login"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Phishing"
    assert data["risk_score"] >= 0.75
    assert len(data["indicators"]) > 0
    assert any("IP address" in ind for ind in data["indicators"])
    assert "Do not click any links" in data["recommended_action"]


def test_high_nlp_score_no_url():
    """Verify message with no URL uses W_nlp=1.00."""
    res = risk_engine.evaluate(
        nlp_score=0.80,
        url_score=0.0,
        has_url=False,
        nlp_indicators=["High phishing intent detected in message text"],
        language_detected="english",
    )
    assert res.classification == ClassificationEnum.PHISHING
    assert res.risk_score == 0.80
    assert res.url_score == 0.0


def test_low_nlp_score_suspicious_url():
    """Verify benign text with highly suspicious URL produces suspicious or phishing score."""
    res = risk_engine.evaluate(
        nlp_score=0.10,
        url_score=0.90,
        has_url=True,
        url_indicators=["IP address used instead of domain name", "Suspicious top-level domain (.xyz)"],
        language_detected="english",
    )
    # (0.60 * 0.10) + (0.40 * 0.90) = 0.06 + 0.36 = 0.42 -> Suspicious
    assert res.classification == ClassificationEnum.SUSPICIOUS
    assert res.risk_score >= 0.40
    assert any("IP address" in ind for ind in res.indicators)


def test_multiple_urls_aggregation_via_api():
    """Verify multiple URLs in payload are analyzed and max URL threat is captured."""
    response = client.post(
        "/api/v1/analyze",
        json={"content": "Visit https://legit-site.gov.in and verify at http://103.21.244.0:8080/fake-kyc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] in ["Suspicious", "Phishing"]
    assert any("IP address" in ind for ind in data["indicators"])


def test_malformed_url_in_message_via_api():
    """Verify malformed link does not crash the system and returns appropriate indicator."""
    response = client.post(
        "/api/v1/analyze",
        json={"content": "Please check your receipt here: http://:::malformed:::"},
    )
    assert response.status_code == 200
    data = response.json()
    assert any("Malformed link detected" in ind for ind in data["indicators"])


def test_native_kannada_phishing_via_api():
    """Verify native Kannada phishing text is classified correctly with Kannada language tag."""
    kannada_text = "ಪ್ರಿಯ ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ SBI ಖಾತೆಯನ್ನು ತಕ್ಷಣ KYC ಅಪ್‌ಡೇಟ್ ಮಾಡಿ: http://sbi-kyc-update.xyz/login"
    response = client.post("/api/v1/analyze", json={"content": kannada_text})
    assert response.status_code == 200
    data = response.json()
    assert data["language_detected"] == "kannada"
    assert data["classification"] == "Phishing"
    assert data["risk_score"] >= 0.75


def test_transliterated_kannada_phishing_via_api():
    """Verify Kanglish phishing message is classified correctly."""
    kanglish_text = "Grahakare, nimma SBI account ivattu block agatte. Koodale PAN update madi http://sbi-pan-kyc.in"
    response = client.post("/api/v1/analyze", json={"content": kanglish_text})
    assert response.status_code == 200
    data = response.json()
    assert data["language_detected"] in ["kannada", "code-mixed"]
    assert data["classification"] in ["Suspicious", "Phishing"]


def test_code_mixed_phishing_via_api():
    """Verify Kannada-English code-mixed input is detected as code-mixed."""
    codemixed_text = "HDFC Alert: Net banking deactivate aytu. Urgent agi Aadhaar verify madi link alli http://hdfc-verify.com"
    response = client.post("/api/v1/analyze", json={"content": codemixed_text})
    assert response.status_code == 200
    data = response.json()
    assert data["language_detected"] == "code-mixed"


def test_model_failure_fallback_degraded_response():
    """Verify system gracefully degrades to Suspicious when ML model inference fails."""
    with patch("backend.app.services.nlp_service.NLPService.analyze") as mock_analyze:
        mock_analyze.return_value = {
            "nlp_score": 0.50,
            "language_detected": "english",
            "script": "latin",
            "is_degraded": True,
            "is_url_only": False,
            "indicators": ["Analysis partially degraded."],
        }

        response = client.post(
            "/api/v1/analyze",
            json={"content": "Important notice regarding your electricity connection."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["classification"] == "Suspicious"
        assert data["risk_score"] >= 0.50
        assert "Analysis partially degraded." in data["indicators"]
        assert "partial degradation" in data["recommended_action"]


def test_ssrf_safety_offline_verification():
    """Verify that private IP / localhost URLs never trigger outbound HTTP connections."""
    with patch("http.client.HTTPConnection.connect") as mock_http, \
         patch("urllib.request.urlopen") as mock_urlopen:

        response = client.post(
            "/api/v1/analyze",
            json={"content": "Access private portal: http://169.254.169.254/latest/meta-data/"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "classification" in data
        mock_http.assert_not_called()
        mock_urlopen.assert_not_called()
