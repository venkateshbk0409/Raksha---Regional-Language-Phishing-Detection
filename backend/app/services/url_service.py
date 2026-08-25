"""Local Lexical URL Parser and Feature Extractor for Raksha.

Conforms strictly to:
- url-analysis-and-risk-engine.md: Local lexical inspection using urllib.parse,
  IP domain detection, suspicious TLD, excessive subdomains, excessive hyphens,
  suspicious path patterns, homoglyphs, malformed URL handling.
  STRICTLY NO OUTBOUND NETWORK CALLS.
- feature-specification.md: FEAT-05 (Local Lexical URL Track).
- security.md: Zero external network requests, zero SSRF risk.
"""

import ipaddress
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


# Regex pattern to extract URLs from text
URL_EXTRACTION_REGEX = re.compile(
    r"(?:https?://|www\.)[^\s/$.?#].[^\s]*|"
    r"[a-zA-Z0-9.-]+\.(?:com|org|net|in|co|info|biz|xyz|top|site|club|vip|online|live|shop|tech|app|io|me|cc|tk|ml|ga|cf|gq)/[^\s]*",
    re.IGNORECASE,
)

# Common High-Abuse / Suspicious TLDs frequently seen in spam/phishing campaigns
SUSPICIOUS_TLDS: Set[str] = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "work", "click", "buzz",
    "fit", "rest", "shop", "vip", "icu", "loan", "cam", "kim", "country",
    "party", "science", "gdn", "mom", "racing", "date", "faith", "review",
    "trade", "accountant", "download", "stream", "win", "bid",
}

# Suspicious keywords commonly found in phishing URLs
SUSPICIOUS_URL_KEYWORDS: Set[str] = {
    "login", "signin", "verify", "verification", "kyc", "update", "secure",
    "security", "account", "banking", "netbanking", "password", "otp", "aadhaar",
    "pan", "sbi", "hdfc", "icici", "bescom", "hescom", "mescom", "cesc",
    "ebill", "electricity", "disconnection", "bill", "refund", "reward",
    "claim", "lottery", "gift", "bonus", "free", "apk", "telegram",
}

# Standard HTTP/HTTPS ports
STANDARD_PORTS: Set[int] = {80, 443}


@dataclass
class UrlLexicalFeatures:
    """Detailed lexical structural features of a single URL."""
    raw_url: str
    scheme: str
    host: str
    port: Optional[int]
    path: str
    query: str
    url_length: int
    host_length: int
    is_ip: bool
    is_https: bool
    subdomain_count: int
    hyphen_count: int
    has_at_symbol: bool
    has_encoded_chars: bool
    has_homoglyphs: bool
    has_suspicious_tld: bool
    suspicious_keywords_found: List[str]
    has_non_standard_port: bool
    is_malformed: bool
    risk_score: float
    indicators: List[str]


@dataclass
class UrlAnalysisResult:
    """Aggregated analysis result for all URLs in an input string."""
    has_url: bool
    url_count: int
    urls: List[str]
    url_score: float
    indicators: List[str]
    features_list: List[UrlLexicalFeatures]
    is_malformed: bool = False


class LocalUrlLexicalParser:
    """Deterministic local-only lexical URL analyzer.
    
    NEVER makes outbound network calls, DNS requests, or API queries.
    """

    def __init__(self):
        self.suspicious_tlds = SUSPICIOUS_TLDS
        self.suspicious_keywords = SUSPICIOUS_URL_KEYWORDS

    def extract_urls(self, text: Optional[str]) -> List[str]:
        """Extracts candidate URLs from raw input text."""
        if not text or not str(text).strip():
            return []
        matches = URL_EXTRACTION_REGEX.findall(str(text))
        # Strip trailing punctuation that often attaches to URLs in text (. , ! ? ) > ] ;)
        clean_urls = []
        for match in matches:
            cleaned = re.sub(r"[.,!?;:)>\]]+$", "", match.strip())
            if cleaned:
                clean_urls.append(cleaned)
        return clean_urls

    def is_ip_address(self, hostname: str) -> bool:
        """Determines if the hostname is a valid IPv4 or IPv6 address."""
        if not hostname:
            return False
        # Strip brackets from IPv6
        clean_host = hostname.strip("[]")
        try:
            ipaddress.ip_address(clean_host)
            return True
        except ValueError:
            return False

    def check_homoglyphs(self, host: str) -> bool:
        """Checks for Punycode (IDN) or mixed-script homoglyphs in hostname."""
        if not host:
            return False
        # Punycode prefix
        if host.lower().startswith("xn--") or ".xn--" in host.lower():
            return True
        # Check for non-ASCII characters in domain host
        try:
            host.encode("ascii")
            return False
        except UnicodeEncodeError:
            # Contains non-ASCII unicode characters in domain
            return True

    def analyze_single_url(self, raw_url: str) -> UrlLexicalFeatures:
        """Performs comprehensive local lexical analysis on a single URL string."""
        indicators: List[str] = []
        score = 0.0

        if not raw_url or not raw_url.strip():
            return UrlLexicalFeatures(
                raw_url=raw_url,
                scheme="",
                host="",
                port=None,
                path="",
                query="",
                url_length=0,
                host_length=0,
                is_ip=False,
                is_https=False,
                subdomain_count=0,
                hyphen_count=0,
                has_at_symbol=False,
                has_encoded_chars=False,
                has_homoglyphs=False,
                has_suspicious_tld=False,
                suspicious_keywords_found=[],
                has_non_standard_port=False,
                is_malformed=True,
                risk_score=0.0,
                indicators=["Malformed link detected"],
            )

        # Prepend scheme if missing (e.g. "www.example.com/path" -> "http://www.example.com/path")
        url_to_parse = raw_url.strip()
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url_to_parse):
            url_to_parse = "http://" + url_to_parse

        try:
            parsed = urllib.parse.urlsplit(url_to_parse)
        except Exception:
            return UrlLexicalFeatures(
                raw_url=raw_url,
                scheme="",
                host="",
                port=None,
                path="",
                query="",
                url_length=len(raw_url),
                host_length=0,
                is_ip=False,
                is_https=False,
                subdomain_count=0,
                hyphen_count=0,
                has_at_symbol=False,
                has_encoded_chars=False,
                has_homoglyphs=False,
                has_suspicious_tld=False,
                suspicious_keywords_found=[],
                has_non_standard_port=False,
                is_malformed=True,
                risk_score=0.0,
                indicators=["Malformed link detected"],
            )

        scheme = (parsed.scheme or "").lower()
        netloc = parsed.netloc or ""
        path = parsed.path or ""
        query = parsed.query or ""

        # Extract hostname and port safely
        try:
            hostname = parsed.hostname or ""
        except ValueError:
            hostname = netloc.split("@")[-1].split(":")[0]

        # If netloc or hostname is completely empty or invalid, treat as malformed
        if not netloc or not hostname or ":::" in raw_url:
            return UrlLexicalFeatures(
                raw_url=raw_url,
                scheme=scheme,
                host=hostname,
                port=None,
                path=path,
                query=query,
                url_length=len(raw_url),
                host_length=len(hostname),
                is_ip=False,
                is_https=False,
                subdomain_count=0,
                hyphen_count=0,
                has_at_symbol=False,
                has_encoded_chars=False,
                has_homoglyphs=False,
                has_suspicious_tld=False,
                suspicious_keywords_found=[],
                has_non_standard_port=False,
                is_malformed=True,
                risk_score=0.0,
                indicators=["Malformed link detected"],
            )

        port = parsed.port
        url_length = len(raw_url)
        host_length = len(hostname)

        # Rule 1: IP address as domain (+0.40)
        is_ip = self.is_ip_address(hostname)
        if is_ip:
            score += 0.40
            indicators.append("IP address used instead of domain name")

        # Rule 2: Insecure connection (HTTP) (+0.10)
        is_https = (scheme == "https")
        if not is_https and not is_ip:
            score += 0.10
            indicators.append("Insecure connection (HTTP)")

        # Rule 3: Presence of '@' symbol (+0.30)
        has_at_symbol = "@" in raw_url
        if has_at_symbol:
            score += 0.30
            indicators.append("Misleading '@' symbol in URL")

        # Rule 4: Homoglyphs / Punycode (+0.35)
        has_homoglyphs = self.check_homoglyphs(hostname)
        if has_homoglyphs:
            score += 0.35
            indicators.append("Punycode or homoglyph domain detected")

        # Rule 5: Suspicious Top-Level Domain (+0.25)
        has_suspicious_tld = False
        if "." in hostname and not is_ip:
            tld = hostname.split(".")[-1].lower()
            if tld in self.suspicious_tlds:
                has_suspicious_tld = True
                score += 0.25
                indicators.append(f"Suspicious top-level domain (.{tld})")

        # Rule 6: Excessive Subdomains (+0.20)
        # e.g., login.sbi.co.in.attacker.com has 6 labels -> 4 subdomains
        host_parts = hostname.split(".")
        subdomain_count = max(0, len(host_parts) - 2)
        if subdomain_count >= 3 and not is_ip:
            score += 0.20
            indicators.append("Excessive subdomains in URL")

        # Rule 7: Excessive Hyphens in hostname (+0.15)
        hyphen_count = hostname.count("-")
        if hyphen_count >= 2:
            score += 0.15
            indicators.append("Excessive hyphens in domain name")

        # Rule 8: Obfuscated / Encoded Characters (+0.15)
        has_encoded_chars = "%" in raw_url
        if has_encoded_chars:
            score += 0.15
            indicators.append("Obfuscated or percent-encoded characters in URL")

        # Rule 9: Non-standard Port (+0.15)
        has_non_standard_port = False
        if port is not None and port not in STANDARD_PORTS:
            has_non_standard_port = True
            score += 0.15
            indicators.append(f"Non-standard network port ({port}) in URL")

        # Rule 10: Suspicious Keywords in Path / Query / Domain (+0.20)
        url_lower = raw_url.lower()
        keywords_found = []
        for kw in self.suspicious_keywords:
            if kw in url_lower:
                keywords_found.append(kw)

        if keywords_found:
            score += min(0.25, 0.10 * len(keywords_found))
            indicators.append("Suspicious security/banking keywords in URL")

        # Rule 11: Unusually long URL length (>75 chars) (+0.10)
        if url_length > 75:
            score += 0.10
            indicators.append("Unusually long URL")

        # Clamp final score to [0.0, 1.0]
        final_score = round(min(1.0, max(0.0, score)), 4)

        return UrlLexicalFeatures(
            raw_url=raw_url,
            scheme=scheme,
            host=hostname,
            port=port,
            path=path,
            query=query,
            url_length=url_length,
            host_length=host_length,
            is_ip=is_ip,
            is_https=is_https,
            subdomain_count=subdomain_count,
            hyphen_count=hyphen_count,
            has_at_symbol=has_at_symbol,
            has_encoded_chars=has_encoded_chars,
            has_homoglyphs=has_homoglyphs,
            has_suspicious_tld=has_suspicious_tld,
            suspicious_keywords_found=keywords_found,
            has_non_standard_port=has_non_standard_port,
            is_malformed=False,
            risk_score=final_score,
            indicators=indicators,
        )

    def analyze(self, text: Optional[str]) -> UrlAnalysisResult:
        """Full lexical analysis on all URLs extracted from an input text."""
        if not text or not str(text).strip():
            return UrlAnalysisResult(
                has_url=False,
                url_count=0,
                urls=[],
                url_score=0.0,
                indicators=[],
                features_list=[],
                is_malformed=False,
            )

        urls = self.extract_urls(text)
        if not urls:
            return UrlAnalysisResult(
                has_url=False,
                url_count=0,
                urls=[],
                url_score=0.0,
                indicators=[],
                features_list=[],
                is_malformed=False,
            )

        features_list = []
        max_score = 0.0
        all_indicators: List[str] = []
        is_any_malformed = False

        for url in urls:
            feat = self.analyze_single_url(url)
            features_list.append(feat)
            if feat.is_malformed:
                is_any_malformed = True
            if feat.risk_score > max_score:
                max_score = feat.risk_score
            for ind in feat.indicators:
                if ind not in all_indicators:
                    all_indicators.append(ind)

        return UrlAnalysisResult(
            has_url=True,
            url_count=len(urls),
            urls=urls,
            url_score=max_score,
            indicators=all_indicators,
            features_list=features_list,
            is_malformed=is_any_malformed,
        )


# Global singleton instance for clean service consumption
url_parser = LocalUrlLexicalParser()
