"""Unit tests verifying models.src.url_parser integration and offline safety."""

import sys
from pathlib import Path
from unittest.mock import patch
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from models.src.url_parser import LocalUrlLexicalParser, url_parser


def test_models_url_parser_singleton():
    """Verify singleton instance parses correctly."""
    res = url_parser.analyze("Click http://192.168.1.1/update-kyc")
    assert res.has_url is True
    assert res.url_score >= 0.40
    assert any("IP address" in ind for ind in res.indicators)


def test_models_url_parser_no_urls():
    """Verify text with no URL returns 0.0 url_score."""
    res = url_parser.analyze("ನಮಸ್ಕಾರ, ದಯವಿಟ್ಟು ನಾಳೆ ಭೇಟಿಯಾಗೋಣ.")
    assert res.has_url is False
    assert res.url_score == 0.0
