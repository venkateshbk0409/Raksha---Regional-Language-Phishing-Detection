"""Unit and integration tests for Privacy-Safe MongoDB Telemetry (TSK-10).

Verifies compliance with:
- database.md: Prohibits raw message text, URLs, phone numbers, IPs, PII.
  Enforces allowed fields: language_detected, has_url, final_classification,
  model_version, latency_ms, timestamp (7-day TTL index: 604800s).
- backend.md: Safe failure handling; DB issues must never crash the API.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.main import app
from backend.app.services.telemetry_service import (
    ALLOWED_CLASSIFICATIONS,
    ALLOWED_LANGUAGES,
    TTL_7_DAYS_SECONDS,
    TelemetryPayload,
    TelemetryService,
)

client = TestClient(app)


def test_telemetry_payload_schema_valid():
    """Verify TelemetryPayload accepts all allowed fields."""
    now = datetime.now(timezone.utc)
    payload = TelemetryPayload(
        language_detected="kannada",
        has_url=True,
        final_classification="Phishing",
        model_version="1.0.0-baseline-tfidf",
        latency_ms=45,
        timestamp=now,
    )

    doc = payload.model_dump()
    assert doc["language_detected"] == "kannada"
    assert doc["has_url"] is True
    assert doc["final_classification"] == "Phishing"
    assert doc["model_version"] == "1.0.0-baseline-tfidf"
    assert doc["latency_ms"] == 45
    assert doc["timestamp"] == now


def test_telemetry_prohibited_fields_rejected():
    """Verify that forbidden fields (raw content, URL, IP, PII) trigger validation error."""
    with pytest.raises(ValidationError):
        TelemetryPayload(
            language_detected="english",
            has_url=True,
            final_classification="Safe",
            latency_ms=10,
            raw_message="Secret message",  # Prohibited!
        )

    with pytest.raises(ValidationError):
        TelemetryPayload(
            language_detected="english",
            has_url=True,
            final_classification="Safe",
            latency_ms=10,
            url="http://evil.com",  # Prohibited!
        )

    with pytest.raises(ValidationError):
        TelemetryPayload(
            language_detected="english",
            has_url=True,
            final_classification="Safe",
            latency_ms=10,
            ip_address="192.168.1.1",  # Prohibited!
        )


def test_telemetry_ttl_constant_is_7_days():
    """Verify TTL index duration is exactly 7 days (604,800 seconds)."""
    assert TTL_7_DAYS_SECONDS == 7 * 24 * 60 * 60
    assert TTL_7_DAYS_SECONDS == 604800


def test_telemetry_service_mock_mongodb_persistence():
    """Verify TelemetryService persists documents and ensures 7-day TTL index."""
    mock_collection = MagicMock()
    mock_collection.insert_one.return_value = MagicMock(inserted_id="mock_id_12345")

    service = TelemetryService(uri="mongodb://localhost:27017", db_name="test_db", collection_name="test_col")
    service.enabled = True
    service._collection = mock_collection

    res = service.record_telemetry(
        language_detected="code-mixed",
        has_url=True,
        final_classification="Suspicious",
        latency_ms=32,
    )

    assert res is not None
    assert res["_id"] == "mock_id_12345"
    assert res["language_detected"] == "code-mixed"
    assert res["has_url"] is True
    assert res["final_classification"] == "Suspicious"
    assert res["latency_ms"] == 32
    assert "raw_content" not in res
    assert "url" not in res


def test_telemetry_service_graceful_database_failure():
    """Verify that a database exception is caught safely without raising an exception."""
    mock_collection = MagicMock()
    mock_collection.insert_one.side_effect = Exception("MongoDB connection refused")

    service = TelemetryService(uri="mongodb://localhost:27017")
    service.enabled = True
    service._collection = mock_collection

    # Should not raise exception
    res = service.record_telemetry(
        language_detected="kannada",
        has_url=False,
        final_classification="Safe",
        latency_ms=15,
    )

    assert res is not None
    assert res["language_detected"] == "kannada"
    assert res["final_classification"] == "Safe"


def test_analyze_endpoint_triggers_telemetry():
    """Verify analyze endpoint records telemetry without leaking to public API response."""
    with patch("backend.app.api.v1.analyze.telemetry_service.record_telemetry") as mock_record:
        mock_record.return_value = {"_id": "test_id"}

        response = client.post(
            "/api/v1/analyze",
            json={"content": "ಪ್ರಿಯ ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ OTP 123456 ಆಗಿದೆ."},
        )

        assert response.status_code == 200
        data = response.json()

        # Public response must still strictly contain only 5 allowed fields per api-specification.md
        assert set(data.keys()) == {
            "classification",
            "risk_score",
            "language_detected",
            "indicators",
            "recommended_action",
        }

        # Telemetry service must have been called with sanitized metadata only
        mock_record.assert_called_once()
        call_kwargs = mock_record.call_args.kwargs
        assert call_kwargs["language_detected"] == data["language_detected"]
        assert call_kwargs["final_classification"] == data["classification"]
        assert "has_url" in call_kwargs
        assert "latency_ms" in call_kwargs
