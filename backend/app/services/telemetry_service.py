"""Privacy-Safe Telemetry Persistence Service (MongoDB Atlas).

Adheres strictly to:
- database.md: Prohibits raw message text, URLs, IPs, phone numbers, and PII.
  Allows ONLY: _id, language_detected, has_url, final_classification,
  model_version, latency_ms, timestamp (with 7-day TTL index).
- backend.md: Safe failure handling. Database failures must NEVER crash the API.
- security.md: No sensitive data logged or leaked.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Allowed classification values
ALLOWED_CLASSIFICATIONS = {"Safe", "Suspicious", "Phishing"}
ALLOWED_LANGUAGES = {"kannada", "english", "code-mixed", "unknown"}
TTL_7_DAYS_SECONDS = 7 * 24 * 60 * 60  # 604,800 seconds (7-day TTL per database.md)


class TelemetryPayload(BaseModel):
    """Strict privacy-safe telemetry record schema conforming to database.md."""

    language_detected: str = Field(..., description="Detected script/language")
    has_url: bool = Field(..., description="Whether URL was present in input")
    final_classification: str = Field(..., description="Classification outcome")
    model_version: str = Field(default="1.0.0-baseline-tfidf", description="Model version")
    latency_ms: int = Field(..., description="Analysis latency in milliseconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp")

    model_config = {
        "extra": "forbid"  # Strictly forbid unapproved extra fields (PII, raw content, URLs, etc.)
    }


class TelemetryService:
    """Manages privacy-compliant telemetry logging to MongoDB with TTL indexing."""

    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None, collection_name: Optional[str] = None):
        self.uri = uri or settings.MONGODB_URI
        self.db_name = db_name or settings.MONGODB_DB_NAME
        self.collection_name = collection_name or settings.MONGODB_COLLECTION
        self.enabled = settings.ENABLE_TELEMETRY or bool(self.uri)
        self._client = None
        self._collection = None
        self._ttl_index_ensured = False

    def _get_collection(self):
        """Lazily connects to MongoDB and ensures the 7-day TTL index."""
        if not self.enabled or not self.uri:
            return None

        if self._collection is None:
            try:
                from pymongo import MongoClient
                self._client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
                db = self._client[self.db_name]
                self._collection = db[self.collection_name]

                # Ensure 7-day TTL index on 'timestamp' field per database.md
                if not self._ttl_index_ensured:
                    self._collection.create_index("timestamp", expireAfterSeconds=TTL_7_DAYS_SECONDS)
                    self._ttl_index_ensured = True
            except Exception as e:
                logger.warning(f"Failed to initialize MongoDB telemetry connection: {e}")
                return None

        return self._collection

    def record_telemetry(
        self,
        language_detected: str,
        has_url: bool,
        final_classification: str,
        latency_ms: int,
        model_version: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        """Validates and persists a privacy-safe telemetry document.

        Returns the inserted document dict on success, or None if disabled/failed.
        Guarantees that database failures NEVER raise exceptions or interrupt API response.
        """
        # Validate values
        lang = language_detected if language_detected in ALLOWED_LANGUAGES else "unknown"
        classification = final_classification if final_classification in ALLOWED_CLASSIFICATIONS else "Suspicious"
        m_version = model_version or settings.MODEL_VERSION
        ts = timestamp or datetime.now(timezone.utc)
        lat = max(0, int(latency_ms))

        try:
            record = TelemetryPayload(
                language_detected=lang,
                has_url=bool(has_url),
                final_classification=classification,
                model_version=m_version,
                latency_ms=lat,
                timestamp=ts,
            )
        except Exception as e:
            logger.warning(f"Telemetry validation failed: {e}")
            return None

        doc = record.model_dump()

        # If MongoDB is enabled and reachable, persist
        col = self._get_collection()
        if col is not None:
            try:
                insert_res = col.insert_one(doc.copy())
                doc["_id"] = str(insert_res.inserted_id)
                logger.debug(f"Recorded telemetry doc id: {doc['_id']}")
            except Exception as e:
                logger.warning(f"Failed to insert telemetry document to MongoDB: {e}")

        return doc


# Global singleton
telemetry_service = TelemetryService()
