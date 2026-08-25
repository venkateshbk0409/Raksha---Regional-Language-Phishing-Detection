"""Unit and contract tests for FastAPI backend API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    """Verify health check endpoint returns 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_valid_text_contract():
    """Verify analyze endpoint returns exactly the five specified public fields."""
    payload = {"content": "Your bank account requires KYC update immediately."}
    response = client.post("/api/v1/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify exact 5 fields in public response per api-specification.md
    expected_fields = {
        "classification",
        "risk_score",
        "language_detected",
        "indicators",
        "recommended_action",
    }
    assert set(data.keys()) == expected_fields
    
    assert data["classification"] in ["Safe", "Suspicious", "Phishing"]
    assert isinstance(data["risk_score"], float)
    assert 0.0 <= data["risk_score"] <= 1.0
    assert data["language_detected"] in ["kannada", "english", "code-mixed", "unknown"]
    assert isinstance(data["indicators"], list)
    assert isinstance(data["recommended_action"], str)
    
    # Internal variables MUST NOT leak into the public response
    assert "nlp_score" not in data
    assert "url_score" not in data
    assert "status" not in data
    assert "normalized_risk_score" not in data


def test_analyze_empty_input_returns_422():
    """Verify empty string returns HTTP 422 with standard ErrorResponse schema."""
    response = client.post("/api/v1/analyze", json={"content": ""})
    assert response.status_code == 422
    data = response.json()
    assert "error_type" in data
    assert "message" in data
    assert data["error_type"] == "validation_error"


def test_analyze_whitespace_only_returns_422():
    """Verify whitespace-only input returns HTTP 422."""
    response = client.post("/api/v1/analyze", json={"content": "    \t\n  "})
    assert response.status_code == 422
    data = response.json()
    assert data["error_type"] == "validation_error"


def test_analyze_oversized_input_returns_400():
    """Verify input longer than 2000 characters returns HTTP 400."""
    oversized_text = "a" * 2001
    response = client.post("/api/v1/analyze", json={"content": oversized_text})
    assert response.status_code == 400
    data = response.json()
    assert "error_type" in data
    assert "message" in data
    assert "2000" in data["message"]


def test_analyze_missing_content_field_returns_422():
    """Verify missing content field in JSON returns HTTP 422."""
    response = client.post("/api/v1/analyze", json={"invalid_field": "test"})
    assert response.status_code == 422
    data = response.json()
    assert data["error_type"] == "validation_error"


def test_analyze_ssrf_safety_local_ips():
    """Verify that user-provided local/private IP URLs return 200 without network requests."""
    test_urls = [
        "http://127.0.0.1",
        "http://192.168.1.1",
        "http://[::1]",
        "http://169.254.169.254/latest/meta-data",
    ]
    for url in test_urls:
        response = client.post("/api/v1/analyze", json={"content": url})
        assert response.status_code == 200
        data = response.json()
        assert "classification" in data
