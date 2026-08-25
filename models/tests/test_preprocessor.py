"""Focused test suite for TextPreprocessor and Language Detection (TSK-03).

Verifies compliance with:
- ai-ml-system.md (Kannada vs Latin script, contextual transliteration, English token preservation)
- api-specification.md (Language values: "kannada", "english", "code-mixed", "unknown")
- testing-and-evaluation.md (Native Kannada, Transliterated Kannada, Code-mixed, English, URLs)
"""

import pytest
from models.src.preprocessor import TextPreprocessor, preprocessor


@pytest.fixture
def prep():
    return TextPreprocessor()


def test_language_detection_native_kannada(prep):
    """Verify native Kannada script input is detected as 'kannada'."""
    text = "ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ SBI ಖಾತೆಯನ್ನು ತಕ್ಷಣ KYC ಅಪ್‌ಡೇಟ್ ಮಾಡಿ: http://sbi-pan-kyc.in"
    res = prep.preprocess(text)

    assert res.language == "kannada"
    assert res.script == "kannada"
    assert res.kannada_char_ratio > 0.60
    assert len(res.extracted_urls) == 1
    assert res.extracted_urls[0] == "http://sbi-pan-kyc.in"


def test_language_detection_english(prep):
    """Verify English text is detected as 'english'."""
    text = "Dear customer, your bank account has been locked. Verify immediately at http://192.168.1.1/login"
    res = prep.preprocess(text)

    assert res.language == "english"
    assert res.script == "latin"
    assert res.latin_char_ratio > 0.80
    assert len(res.extracted_urls) == 1


def test_language_detection_transliterated_kannada(prep):
    """Verify Latin-script transliterated Kannada (Kanglish) is detected correctly."""
    text = "Grahakare, nimma SBI account ivattu block agatte. Koodale PAN update madi."
    res = prep.preprocess(text)

    # Transliterated Kannada or code-mixed with strong Kannada indicators
    assert res.language in ["kannada", "code-mixed"]
    assert res.script == "latin"
    assert res.latin_char_ratio > 0.80


def test_language_detection_code_mixed(prep):
    """Verify code-mixed Kannada-English input is detected as 'code-mixed'."""
    text = "HDFC Alert: Net banking deactivate aytu. Urgent agi Aadhaar verify madi link alli http://hdfc-verify.com"
    res = prep.preprocess(text)

    assert res.language == "code-mixed"
    assert res.script == "latin"


def test_empty_and_whitespace_input(prep):
    """Verify empty or whitespace-only inputs are handled gracefully."""
    for empty_val in ["", "   ", "\t\n  ", None]:
        res = prep.preprocess(empty_val)
        assert res.is_empty is True
        assert res.language == "unknown"
        assert res.script == "unknown"
        assert res.cleaned_text == ""
        assert res.tokens == []


def test_numeric_and_symbolic_input(prep):
    """Verify numbers and symbols return 'unknown' language."""
    res_num = prep.preprocess("9845123456 1234 5678")
    assert res_num.language == "unknown"

    res_sym = prep.preprocess("!@#$%^&*() _+=-<>?")
    assert res_sym.language == "unknown"


def test_unicode_sanitization(prep):
    """Verify non-printable control characters are stripped and Unicode normalized to NFC."""
    # String containing null byte and control character
    dirty_text = "ಗ್ರಾಹಕರೇ\x00, ನಿಮ್ಮ ಖಾತೆ\x07 ಸಕ್ರಿಯವಾಗಿದೆ."
    res = prep.preprocess(dirty_text)

    assert "\x00" not in res.cleaned_text
    assert "\x07" not in res.cleaned_text
    assert "ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ ಖಾತೆ ಸಕ್ರಿಯವಾಗಿದೆ." in res.cleaned_text


def test_english_token_preservation_in_transliteration(prep):
    """Verify English technical words are preserved while high-confidence Kanglish words are standardized."""
    text = "nimma SBI account update madi koodale"
    res = prep.preprocess(text)

    # English keywords preserved in lower case
    assert "sbi" in res.normalized_tokens
    assert "account" in res.normalized_tokens
    assert "update" in res.normalized_tokens

    # High-confidence Kanglish normalized to Kannada script
    assert "ನಿಮ್ಮ" in res.normalized_tokens
    assert "ಮಾಡಿ" in res.normalized_tokens
    assert "ಕೂಡಲೇ" in res.normalized_tokens


def test_url_extraction(prep):
    """Verify URLs are extracted correctly without destroying surrounding tokens."""
    text = "Click http://bescom-bill.in/pay and check www.kptcl.gov.in for updates"
    res = prep.preprocess(text)

    assert len(res.extracted_urls) == 2
    assert "http://bescom-bill.in/pay" in res.extracted_urls
    assert "www.kptcl.gov.in" in res.extracted_urls


def test_deterministic_preprocessing(prep):
    """Verify multiple executions on identical input yield identical results."""
    text = "Dear customer, nimma account block agatte within 2 hours."
    res1 = prep.preprocess(text)
    res2 = prep.preprocess(text)

    assert res1.language == res2.language
    assert res1.script == res2.script
    assert res1.cleaned_text == res2.cleaned_text
    assert res1.tokens == res2.tokens
    assert res1.normalized_tokens == res2.normalized_tokens
    assert res1.kannada_char_ratio == res2.kannada_char_ratio
