"""End-to-end scenario verification suite for Raksha.

Validates complete system pipeline:
Input Text/URL -> Router -> URL Lexical Parser -> NLP Classifier -> Risk Engine -> Telemetry -> Response
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_scenario_native_kannada_phishing():
    """Scenario 1: Native Kannada SBI KYC phishing with IP host link."""
    payload = {
        "content": "ಪ್ರಿಯ ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ SBI ಖಾತೆಯನ್ನು ತಕ್ಷಣ KYC ಅಪ್‌ಡೇಟ್ ಮಾಡಿ ಇಲ್ಲವಾದರೆ ಖಾತೆ 24 ಗಂಟೆಯಲ್ಲಿ ಬ್ಲಾಕ್ ಆಗುತ್ತದೆ: http://192.168.1.100/sbi/kyc"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["classification"] == "Phishing"
    assert data["risk_score"] >= 0.75
    assert data["language_detected"] == "kannada"
    assert any("IP address" in ind for ind in data["indicators"])
    assert len(data["recommended_action"]) > 0


def test_scenario_kanglish_urgency_phishing():
    """Scenario 2: Latin-script transliterated Kannada (Kanglish) electricity cut threat."""
    payload = {
        "content": "Nimma BESCOM electricity bill koodale pay madi, illadiddare current cut agutte: http://bescom-bill-pay.xyz/login"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["classification"] in {"Phishing", "Suspicious"}
    assert data["risk_score"] >= 0.40
    assert data["language_detected"] in {"kannada", "code-mixed"}
    assert any("top-level domain" in ind or ".xyz" in ind for ind in data["indicators"])


def test_scenario_codemixed_reward_phishing():
    """Scenario 3: Code-mixed lottery scam with @ symbol in URL."""
    payload = {
        "content": "Congratulations! You won ₹50,000 cash prize from KBC lottery. Claim your reward immediately: http://kbc-official@lottery-winner-reward.top/claim"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["classification"] == "Phishing"
    assert data["risk_score"] >= 0.75
    assert any("Userinfo" in ind or "@" in ind or "top-level domain" in ind for ind in data["indicators"])


def test_scenario_benign_kannada_otp():
    """Scenario 4: Legitimate Kannada bank OTP alert (no links)."""
    payload = {
        "content": "ಪ್ರಿಯ ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆಯ ಲಾಗಿನ್ OTP 584920 ಆಗಿದೆ. ಇದನ್ನು ಯಾರೊಂದಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ."
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["classification"] == "Safe"
    assert data["risk_score"] < 0.40
    assert data["language_detected"] == "kannada"
    assert data["indicators"] == []


def test_scenario_benign_english_receipt():
    """Scenario 5: Legitimate English utility receipt with benign HTTPS link."""
    payload = {
        "content": "Thank you for your payment of ₹1,450 for BESCOM electricity bill. View official receipt at https://bescom.karnataka.gov.in/receipt"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["classification"] == "Safe"
    assert data["risk_score"] < 0.40
    assert data["language_detected"] == "english"


def test_scenario_url_only_suspicious():
    """Scenario 6: Standalone URL input with excessive subdomains and IP."""
    payload = {
        "content": "http://secure.login.update.account.verify.192.168.1.1.xyz/auth"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["classification"] in {"Phishing", "Suspicious"}
    assert data["risk_score"] >= 0.40
    assert len(data["indicators"]) > 0


def test_scenario_max_length_boundary_2000():
    """Scenario 7: Exactly 2000 character boundary test."""
    content = "A" * 2000
    assert len(content) == 2000

    response = client.post("/api/v1/analyze", json={"content": content})
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert 0.0 <= data["risk_score"] <= 1.0


def test_scenario_oversized_2001_rejected():
    """Scenario 8: 2001 characters must return HTTP 400."""
    content = "A" * 2001
    response = client.post("/api/v1/analyze", json={"content": content})
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "validation_error"


# ==============================================================================
# BENCHMARK VERIFICATION SUITE (10 Real-World Diagnostic Cases)
# ==============================================================================

def test_benchmark_case_1_fake_bank_kyc():
    """Test 1: Fake bank KYC with .xyz link -> Phishing (>= 0.75)."""
    text = "Your SBI account will be blocked today due to incomplete KYC verification. Update your details immediately at http://sbi-verify-account.xyz/kyc to avoid suspension."
    response = client.post("/api/v1/analyze", json={"content": text})
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Phishing"
    assert data["risk_score"] >= 0.75


def test_benchmark_case_2_fake_courier():
    """Test 2: Fake courier parcel payment -> Phishing (>= 0.75)."""
    text = "Your parcel could not be delivered. Pay ₹25 for the pending delivery charge and confirm your address here: http://delivery-confirm.xyz/pay"
    response = client.post("/api/v1/analyze", json={"content": text})
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Phishing"
    assert data["risk_score"] >= 0.75


def test_benchmark_case_3_fake_electricity_bill():
    """Test 3: Fake electricity bill cutoff threat -> Phishing (>= 0.75)."""
    text = "BESCOM: Your electricity connection will be disconnected within 2 hours due to an unpaid bill. Pay immediately: http://bescom-payment.xyz"
    response = client.post("/api/v1/analyze", json={"content": text})
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Phishing"
    assert data["risk_score"] >= 0.75


def test_benchmark_case_4_kannada_phishing():
    """Test 4: Native Kannada bank KYC block scam -> Phishing (>= 0.75)."""
    text = "ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆ KYC ಅಪ್ಡೇಟ್ ಆಗಿಲ್ಲ. ಖಾತೆ ಬಂದ್ ಆಗುವುದನ್ನು ತಪ್ಪಿಸಲು ತಕ್ಷಣ ಈ ಲಿಂಕ್ ಕ್ಲಿಕ್ ಮಾಡಿ: http://bank-kyc.xyz"
    response = client.post("/api/v1/analyze", json={"content": text})
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Phishing"
    assert data["risk_score"] >= 0.75
    assert data["language_detected"] == "kannada"


def test_benchmark_case_5_kanglish_phishing():
    """Test 5: Kanglish power cut threat -> Phishing (>= 0.75)."""
    text = "Nimma current bill pending ide. Ivattu payment madilla andre current disconnect agutte. Iga ee link open madi: http://payment-verify.xyz"
    response = client.post("/api/v1/analyze", json={"content": text})
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Phishing"
    assert data["risk_score"] >= 0.75
    assert data["language_detected"] in ["kannada", "code-mixed"]


def test_benchmark_case_6_suspicious_without_url():
    """Test 6: Suspicious message without URL -> Suspicious (0.40 - 0.74)."""
    text = "Your account requires immediate verification. Please contact the support team today to prevent interruption of service."
    response = client.post("/api/v1/analyze", json={"content": text})
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Suspicious"
    assert 0.40 <= data["risk_score"] < 0.75


def test_benchmark_case_7_reward_shortened_link():
    """Test 7: Reward claim with shortened bit.ly link -> Suspicious or Phishing."""
    text = "Your reward is ready! Confirm your details to receive the amount: bit.ly/claim-reward"
    response = client.post("/api/v1/analyze", json={"content": text})
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] in ["Suspicious", "Phishing"]
    assert data["risk_score"] >= 0.40
    assert any("shortening" in ind.lower() for ind in data["indicators"])


def test_benchmark_case_8_legit_electricity_reminder():
    """Test 8: Legitimate electricity overdue reminder -> Safe or Suspicious (< 0.75)."""
    text = "Your electricity bill is overdue. Please complete the payment today to avoid late fees."
    response = client.post("/api/v1/analyze", json={"content": text})
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] in ["Safe", "Suspicious"]
    assert data["risk_score"] < 0.75


def test_benchmark_case_9_normal_bank_notification():
    """Test 9: Normal bank credit alert with official number advice -> Safe (< 0.40)."""
    text = "Your account ending in 4821 was credited with ₹5,000 on 27 Aug 2026. If you did not make this transaction, contact your bank using the official number."
    response = client.post("/api/v1/analyze", json={"content": text})
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Safe"
    assert data["risk_score"] < 0.40


def test_benchmark_case_10_normal_delivery_notification():
    """Test 10: Normal shopping delivery notification -> Safe (< 0.40)."""
    text = "Your order has been shipped and is expected to arrive tomorrow. You can check the delivery status in the official shopping app."
    response = client.post("/api/v1/analyze", json={"content": text})
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] == "Safe"
    assert data["risk_score"] < 0.40
