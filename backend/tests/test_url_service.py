"""Automated test suite for LocalUrlLexicalParser (TSK-05).

Verifies compliance with:
- url-analysis-and-risk-engine.md (Local lexical analysis, 0.0-1.0 score range, indicators)
- feature-specification.md (FEAT-05)
- security.md (Strict offline operation, 0 network calls, SSRF safety)
"""

import sys
from pathlib import Path
from unittest.mock import patch
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.services.url_service import LocalUrlLexicalParser, url_parser


@pytest.fixture
def parser():
    return LocalUrlLexicalParser()


def test_normal_https_url(parser):
    """Verify normal benign HTTPS URL has low risk score and no high-risk indicators."""
    res = parser.analyze("Please visit our portal at https://www.karnataka.gov.in/services")
    assert res.has_url is True
    assert res.url_count == 1
    assert res.url_score < 0.20
    feat = res.features_list[0]
    assert feat.is_https is True
    assert feat.is_ip is False
    assert feat.has_at_symbol is False


def test_insecure_http_url(parser):
    """Verify plain HTTP URL triggers insecure connection indicator."""
    res = parser.analyze("Check website http://mysite-example.com/welcome")
    assert res.has_url is True
    assert any("Insecure connection (HTTP)" in ind for ind in res.indicators)
    feat = res.features_list[0]
    assert feat.is_https is False


def test_ip_address_host(parser):
    """Verify IP address used as hostname is flagged as high risk."""
    for ip_url in [
        "http://192.168.1.1/admin",
        "http://103.21.244.0:8080/sbi-kyc",
        "http://[2001:db8::1]/login",
    ]:
        res = parser.analyze(f"Click here: {ip_url}")
        assert res.has_url is True
        assert res.url_score >= 0.40
        assert any("IP address used instead of domain name" in ind for ind in res.indicators)
        assert res.features_list[0].is_ip is True


def test_excessive_subdomains(parser):
    """Verify multiple subdomains trigger excessive subdomains indicator."""
    url = "http://login.secure.sbi.co.in.attacker-host.com/verify"
    res = parser.analyze(f"Update your account at {url}")
    assert res.has_url is True
    assert any("Excessive subdomains in URL" in ind for ind in res.indicators)
    assert res.features_list[0].subdomain_count >= 3


def test_suspicious_long_path_and_query(parser):
    """Verify long path and suspicious security keywords in path/query."""
    url = "https://example-site.com/deep/path/verify/kyc/update/aadhaar?token=1234567890&session=abcdef"
    res = parser.analyze(f"Click {url}")
    assert res.has_url is True
    assert any("Suspicious security/banking keywords in URL" in ind for ind in res.indicators)
    assert "kyc" in res.features_list[0].suspicious_keywords_found
    assert "verify" in res.features_list[0].suspicious_keywords_found


def test_at_symbol_in_url(parser):
    """Verify presence of @ symbol in URL is flagged."""
    url = "http://sbi.co.in@evil-attacker.com/login"
    res = parser.analyze(f"Banking login: {url}")
    assert res.has_url is True
    assert any("Misleading '@' symbol in URL" in ind for ind in res.indicators)
    assert res.features_list[0].has_at_symbol is True


def test_encoded_characters(parser):
    """Verify percent-encoded characters are flagged."""
    url = "http://evil-site.com/%2e%2e/login%20verify%40update"
    res = parser.analyze(f"Access link: {url}")
    assert res.has_url is True
    assert any("Obfuscated or percent-encoded characters in URL" in ind for ind in res.indicators)
    assert res.features_list[0].has_encoded_chars is True


def test_suspicious_tld(parser):
    """Verify high-abuse/suspicious TLDs are flagged."""
    for tld in ["xyz", "top", "tk", "click", "vip"]:
        url = f"http://sbi-secure-update.{tld}/login"
        res = parser.analyze(f"Click here: {url}")
        assert res.has_url is True
        assert any(f"Suspicious top-level domain (.{tld})" in ind for ind in res.indicators)
        assert res.features_list[0].has_suspicious_tld is True


def test_malformed_url_handling(parser):
    """Verify malformed or unparseable URLs do not crash the parser."""
    for bad_url in ["http://", "https://", "http://:::malformed:::", ""]:
        feat = parser.analyze_single_url(bad_url)
        assert feat.is_malformed is True
        assert feat.risk_score == 0.0


def test_empty_and_no_url_input(parser):
    """Verify text with no URL returns has_url=False and url_score=0.0."""
    for text in ["", "   ", None, "Namaskara sir, please join tomorrow's team meeting."]:
        res = parser.analyze(text)
        assert res.has_url is False
        assert res.url_count == 0
        assert res.url_score == 0.0
        assert res.indicators == []


def test_multiple_urls_in_single_message(parser):
    """Verify multiple URLs are all analyzed and max risk score is aggregated."""
    text = "Check http://bescom-bill.in/pay and http://192.168.1.1/fake-login for receipts."
    res = parser.analyze(text)
    assert res.has_url is True
    assert res.url_count == 2
    assert len(res.features_list) == 2
    # IP url has high score, should drive max url_score
    assert res.url_score >= 0.40
    # Indicators from both URLs should be captured
    assert any("IP address used instead of domain name" in ind for ind in res.indicators)


def test_deterministic_repeated_execution(parser):
    """Verify repeated executions on identical input yield identical results."""
    text = "URGENT: http://login.sbi.co.in.attacker.xyz:8080/verify-kyc?id=999"
    res1 = parser.analyze(text)
    res2 = parser.analyze(text)

    assert res1.has_url == res2.has_url
    assert res1.url_count == res2.url_count
    assert res1.url_score == res2.url_score
    assert res1.indicators == res2.indicators
    assert res1.features_list[0].is_ip == res2.features_list[0].is_ip
    assert res1.features_list[0].risk_score == res2.features_list[0].risk_score


def test_ssrf_safety_zero_network_calls(parser):
    """Verify that analyzing URLs never triggers any socket connection or HTTP call."""
    with patch("socket.socket") as mock_socket, \
         patch("urllib.request.urlopen") as mock_urlopen:

        dangerous_urls = [
            "http://127.0.0.1:8000/internal-admin",
            "http://169.254.169.254/latest/meta-data/",
            "http://localhost:3000/secrets",
            "http://private-corp.internal/keys",
        ]
        for d_url in dangerous_urls:
            res = parser.analyze(f"Visit: {d_url}")
            assert res.has_url is True

        # Assert no network calls were attempted
        mock_socket.assert_not_called()
        mock_urlopen.assert_not_called()


def test_url_shortener_detection(parser):
    """Verify common URL shortening domains are detected generically."""
    for shortener_url in ["http://bit.ly/claim-reward", "https://tinyurl.com/xyz123", "http://t.co/abc"]:
        res = parser.analyze(f"Claim now at {shortener_url}")
        assert res.has_url is True
        assert any("shortening service detected" in ind.lower() for ind in res.indicators)
        assert res.features_list[0].is_shortened is True


def test_schemeless_url_extraction(parser):
    """Verify schemeless URLs like bit.ly/path or domain.com/path are extracted."""
    res = parser.analyze("Your reward is ready: bit.ly/claim-reward")
    assert res.has_url is True
    assert res.url_count == 1
    assert "bit.ly/claim-reward" in res.urls
    assert any("shortening" in ind.lower() for ind in res.indicators)
