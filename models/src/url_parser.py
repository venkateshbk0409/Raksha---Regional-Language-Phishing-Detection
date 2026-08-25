"""Local URL Lexical Parser package export for ML pipeline."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.services.url_service import (
    LocalUrlLexicalParser,
    UrlLexicalFeatures,
    UrlAnalysisResult,
    url_parser,
)

__all__ = [
    "LocalUrlLexicalParser",
    "UrlLexicalFeatures",
    "UrlAnalysisResult",
    "url_parser",
]
