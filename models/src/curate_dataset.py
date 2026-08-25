"""Dataset Curation, Augmentation, and Group-Splitting Pipeline for Raksha.

Conforms strictly to ai-ml-system.md:
- Scarcity of real-world Kannada phishing datasets is addressed via multi-source curation.
- Composition: Original English templates, programmatic/contextual Kannada translations,
  and synthetic transliterated (Kanglish) & code-mixed Kannada-English variations.
- Group-Based Splitting: 70% Train, 15% Validation, 15% Test.
  Guarantees 0% group leakage across splits.
- Generates specialized test evaluation subsets for Native Kannada, English,
  Transliterated Kannada, and Code-Mixed text.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


# Directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SUBSETS_DIR = PROCESSED_DATA_DIR / "subsets"


def get_base_message_templates() -> List[Dict]:
    """Curated base message groups representing diverse regional threat vectors and legitimate communications."""
    templates = [
        # ==========================================
        # PHISHING: KYC & Bank Fraud (1-6)
        # ==========================================
        {
            "group_id": "PHISH_KYC_01",
            "category": "kyc_fraud",
            "label": 1,
            "has_url": True,
            "english": "Dear customer, your SBI account will be blocked today due to pending KYC. Update PAN immediately at http://sbi-pan-kyc.in",
            "native_kannada": "ಗ್ರಾಹಕರೇ, KYC ಬಾಕಿ ಇರುವುದರಿಂದ ನಿಮ್ಮ SBI ಖಾತೆಯನ್ನು ಇಂದು ನಿರ್ಬಂಧಿಸಲಾಗುತ್ತದೆ. ತಕ್ಷಣ ಪಾನ್ ಅಪ್‌ಡೇಟ್ ಮಾಡಿ: http://sbi-pan-kyc.in",
            "transliterated": "Grahakare, nimma SBI account ivattu block agatte pending KYC inda. Koodale PAN update madi: http://sbi-pan-kyc.in",
            "codemixed": "Dear customer, nimma SBI bank account suspend agutte today due to KYC. Please click link update madi: http://sbi-pan-kyc.in",
        },
        {
            "group_id": "PHISH_KYC_02",
            "category": "kyc_fraud",
            "label": 1,
            "has_url": True,
            "english": "HDFC Bank Alert: Your net banking is deactivated. Submit Aadhaar verification within 24 hours at http://hdfc-aadhaar-verify.com",
            "native_kannada": "HDFC ಬ್ಯಾಂಕ್ ಎಚ್ಚರಿಕೆ: ನಿಮ್ಮ ನೆಟ್ ಬ್ಯಾಂಕಿಂಗ್ ನಿಷ್ಕ್ರಿಯಗೊಂಡಿದೆ. 24 ಗಂಟೆಗಳಲ್ಲಿ ಆಧಾರ್ ಪರಿಶೀಲನೆ ಸಲ್ಲಿಸಿ: http://hdfc-aadhaar-verify.com",
            "transliterated": "HDFC Bank Alert: Nimma net banking deactivate aagide. 24 ghanteyalli Aadhaar verification maadi: http://hdfc-aadhaar-verify.com",
            "codemixed": "HDFC Alert: Net banking deactivate aytu. Urgent agi Aadhaar verify madi link alli http://hdfc-aadhaar-verify.com or card block agatte.",
        },
        {
            "group_id": "PHISH_KYC_03",
            "category": "kyc_fraud",
            "label": 1,
            "has_url": True,
            "english": "Canara Bank: Your debit card is locked. Fill out the unblocking form to avoid permanent termination: http://canara-unblock-portal.net",
            "native_kannada": "ಕೆನರಾ ಬ್ಯಾಂಕ್: ನಿಮ್ಮ ಡೆಬಿಟ್ ಕಾರ್ಡ್ ಲಾಕ್ ಆಗಿದೆ. ಖಾಯಂ ರದ್ದತಿಯನ್ನು ತಪ್ಪಿಸಲು ಅನ್‌ಬ್ಲಾಕ್ ಫಾರ್ಮ್ ಭರ್ತಿ ಮಾಡಿ: http://canara-unblock-portal.net",
            "transliterated": "Canara Bank: Nimma debit card lock aagide. Khayam raddati thapisalu unblock form fill maadi: http://canara-unblock-portal.net",
            "codemixed": "Canara Bank card locked aagide. Permanent cancel agbeka bedva? Eega unblock madi link: http://canara-unblock-portal.net",
        },
        {
            "group_id": "PHISH_KYC_04",
            "category": "kyc_fraud",
            "label": 1,
            "has_url": True,
            "english": "Bank of Baroda: Urgent KYC re-verification required for active account status. Click http://bob-kyc-desk.org",
            "native_kannada": "ಬ್ಯಾಂಕ್ ಆಫ್ ಬರೋಡಾ: ಸಕ್ರಿಯ ಖಾತೆಗಾಗಿ ತುರ್ತು KYC ಮರುಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ. ಕ್ಲಿಕ್ ಮಾಡಿ: http://bob-kyc-desk.org",
            "transliterated": "Bank of Baroda: Sakriya khathegagi thurthu KYC verification bekaagide. Click maadi: http://bob-kyc-desk.org",
            "codemixed": "Bank of Baroda: Urgent KYC update madlilla andre account close agutte. Link click madi: http://bob-kyc-desk.org",
        },
        {
            "group_id": "PHISH_KYC_05",
            "category": "kyc_fraud",
            "label": 1,
            "has_url": True,
            "english": "Axis Bank: Your mobile number verification is pending. Verify immediately to continue UPI services: http://axis-upi-verify.biz",
            "native_kannada": "ಆಕ್ಸಿಸ್ ಬ್ಯಾಂಕ್: ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಪರಿಶೀಲನೆ ಬಾಕಿ ಇದೆ. UPI ಸೇವೆ ಮುಂದುವರಿಸಲು ತಕ್ಷಣ ಪರಿಶೀಲಿಸಿ: http://axis-upi-verify.biz",
            "transliterated": "Axis Bank: Nimma mobile number verification baki ide. UPI service continue madoke eegale verify madi: http://axis-upi-verify.biz",
            "codemixed": "Axis Bank notice: Mobile number verify aagilla. UPI stop agutte eegale link open madi: http://axis-upi-verify.biz",
        },
        {
            "group_id": "PHISH_KYC_06",
            "category": "kyc_fraud",
            "label": 1,
            "has_url": True,
            "english": "ICICI Alert: Your credit card reward points worth Rs 8,450 will expire tonight. Convert to cash here: http://icici-points-redeem.com",
            "native_kannada": "ICICI ಎಚ್ಚರಿಕೆ: ನಿಮ್ಮ ರೂ 8,450 ಮೌಲ್ಯದ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ ರಿವಾರ್ಡ್ ಪಾಯಿಂಟ್‌ಗಳು ಇಂದು ರಾತ್ರಿ ಮುಕ್ತಾಯಗೊಳ್ಳುತ್ತವೆ. ನಗದಾಗಿ ಪರಿವರ್ತಿಸಿ: http://icici-points-redeem.com",
            "transliterated": "ICICI Alert: Nimma Rs 8,450 reward points ivattu ratri expire agatte. Cash convert madi: http://icici-points-redeem.com",
            "codemixed": "ICICI Credit Card points Rs 8450 expire aaguttide. Claim cash into account quickly: http://icici-points-redeem.com",
        },

        # ==========================================
        # PHISHING: Electricity & Utility Disconnection Threats (7-11)
        # ==========================================
        {
            "group_id": "PHISH_UTIL_01",
            "category": "utility_bill_threat",
            "label": 1,
            "has_url": False,
            "english": "BESCOM Electricity Alert: Your power supply will be disconnected tonight at 9:30 PM due to unpaid bill. Call officer immediately at 9845123456",
            "native_kannada": "ಬೆಸ್ಕಾಂ ಎಚ್ಚರಿಕೆ: ಹಿಂದಿನ ತಿಂಗಳ ಬಿಲ್ ಪಾವತಿಸದ ಕಾರಣ ಇಂದು ರಾತ್ರಿ 9:30 ಕ್ಕೆ ನಿಮ್ಮ ವಿದ್ಯುತ್ ಸಂಪರ್ಕ ಕಡಿತಗೊಳ್ಳಲಿದೆ. ತಕ್ಷಣ ಅಧಿಕಾರಿಗೆ ಕರೆ ಮಾಡಿ: 9845123456",
            "transliterated": "BESCOM Alert: Hinde tingala bill pay madada karana ivattu ratri 9:30 ge power cut madtare. Officer ge call madi: 9845123456",
            "codemixed": "BESCOM warning: Electricity disconnect agatte today 9:30 PM bill pending ide. Urgent call madam/sir at 9845123456.",
        },
        {
            "group_id": "PHISH_UTIL_02",
            "category": "utility_bill_threat",
            "label": 1,
            "has_url": True,
            "english": "MESCOM Department: Power cut scheduled for meter #482910. Clear dues of Rs 1,450 to avoid penalty: http://mescom-bill-clear.in",
            "native_kannada": "ಮೆಸ್ಕಾಂ ಇಲಾಖೆ: ಮೀಟರ್ ಸಂಖ್ಯೆ #482910 ಗೆ ವಿದ್ಯುತ್ ಕಡಿತ ನಿಗದಿಯಾಗಿದೆ. ದಂಡ ತಪ್ಪಿಸಲು ರೂ 1,450 ಪಾವತಿಸಿ: http://mescom-bill-clear.in",
            "transliterated": "MESCOM Ilakhe: Meter no #482910 ge power cut schedule aagide. Danda thapisalu Rs 1,450 kattiri: http://mescom-bill-clear.in",
            "codemixed": "MESCOM Alert: Nimma meter power cut agbeka? Clear Rs 1450 dues instantly at http://mescom-bill-clear.in immediately.",
        },
        {
            "group_id": "PHISH_UTIL_03",
            "category": "utility_bill_threat",
            "label": 1,
            "has_url": True,
            "english": "HESCOM Notice: Your commercial connection will be permanently terminated within 2 hours. Pay online now: http://hescom-pay-fast.com",
            "native_kannada": "ಹೆಸ್ಕಾಂ ಸೂಚನೆ: ನಿಮ್ಮ ವಾಣಿಜ್ಯ ವಿದ್ಯುತ್ ಸಂಪರ್ಕವು 2 ಗಂಟೆಗಳಲ್ಲಿ ಕಡಿತಗೊಳ್ಳುತ್ತದೆ. ಈಗಲೇ ಆನ್‌ಲೈನ್‌ನಲ್ಲಿ ಪಾವತಿಸಿ: http://hescom-pay-fast.com",
            "transliterated": "HESCOM Soochane: Nimma power connection 2 ghanteyalli raddagutte. Eegale online alli pay maadi: http://hescom-pay-fast.com",
            "codemixed": "HESCOM Notice: 2 hours alli power supply stop aagutte. Urgent pay at http://hescom-pay-fast.com without fail.",
        },
        {
            "group_id": "PHISH_UTIL_04",
            "category": "utility_bill_threat",
            "label": 1,
            "has_url": True,
            "english": "GESCOM Warning: Urgent power bill pending. Meter disconnection order issued. Avoid line cutoff by clicking: http://gescom-quickbill.net",
            "native_kannada": "ಜೆಸ್ಕಾಂ ಎಚ್ಚರಿಕೆ: ತುರ್ತು ವಿದ್ಯುತ್ ಬಿಲ್ ಬಾಕಿ ಇದೆ. ಮೀಟರ್ ಸಂಪರ್ಕ ಕಡಿತ ಆದೇಶ ಹೊರಡಿಸಲಾಗಿದೆ. ಕಡಿತ ತಪ್ಪಿಸಲು ಕ್ಲಿಕ್ ಮಾಡಿ: http://gescom-quickbill.net",
            "transliterated": "GESCOM Warning: Thurthu power bill baki ide. Meter disconnect order bandide. Line cutoff thapisalu click madi: http://gescom-quickbill.net",
            "codemixed": "GESCOM alert! Power line cut madoke order aagide. Avoid disconnection right now at http://gescom-quickbill.net",
        },
        {
            "group_id": "PHISH_UTIL_05",
            "category": "utility_bill_threat",
            "label": 1,
            "has_url": False,
            "english": "BWSSB Water Notice: Water supply connection #90218 will be stopped from tomorrow morning due to arrears. Contact helpline 9102938475",
            "native_kannada": "BWSSB ನೀರು ಸರಬರಾಜು ಸೂಚನೆ: ಬಾಕಿ ಹಣ ಪಾವತಿಸದ ಕಾರಣ ನಾಳೆ ಬೆಳಗ್ಗೆಯಿಂದ ನಿಮ್ಮ ನೀರಿನ ಸಂಪರ್ಕ ಸ್ಥಗಿತಗೊಳ್ಳಲಿದೆ. ಸಂಪರ್ಕಿಸಿ: 9102938475",
            "transliterated": "BWSSB Water Notice: Baki hana pay madada karana nale belagge water connection cut madtare. Call madi: 9102938475",
            "codemixed": "BWSSB Water supply connection cut aaguttide tomorrow. Urgent call officer on 9102938475 before 8 PM.",
        },

        # ==========================================
        # PHISHING: Fake Rewards, Lotteries & Schemes (12-16)
        # ==========================================
        {
            "group_id": "PHISH_REW_01",
            "category": "fake_reward_lottery",
            "label": 1,
            "has_url": True,
            "english": "Congratulations! You won Rs 50,000 cash prize in Karnataka State Diwali Lucky Draw. Claim your prize instantly at http://karnataka-lottery-claim.com",
            "native_kannada": "ಅಭಿನಂದನೆಗಳು! ಕರ್ನಾಟಕ ರಾಜ್ಯ ದೀಪಾವಳಿ ಲಕ್ಕಿ ಡ್ರಾದಲ್ಲಿ ನೀವು ರೂ 50,000 ನಗದು ಬಹುಮಾನ ಗೆದ್ದಿದ್ದೀರಿ. ನಿಮ್ಮ ಹಣ ಪಡೆಯಲು ಭೇಟಿ ನೀಡಿ: http://karnataka-lottery-claim.com",
            "transliterated": "Abhinandanegalu! Karnataka State Diwali Lucky Draw nalli neevu Rs 50,000 prize geddidiri. Eegale claim madi: http://karnataka-lottery-claim.com",
            "codemixed": "Congratulations! Nimge Karnataka lottery alli Rs 50000 cash prize bandide. Claim madbeka andre link open madi: http://karnataka-lottery-claim.com",
        },
        {
            "group_id": "PHISH_REW_02",
            "category": "fake_reward_lottery",
            "label": 1,
            "has_url": True,
            "english": "PM Kisan Yojana: Rs 6,000 installment is pending in your bank account. Verify bank details to deposit: http://pmkisan-yojana-credit.org",
            "native_kannada": "ಪಿಎಂ ಕಿಸಾನ್ ಯೋಜನೆ: ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ರೂ 6,000 ಕಂತು ಜಮೆಯಾಗಲು ಬಾಕಿ ಇದೆ. ಹಣ ಪಡೆಯಲು ವಿವರ ನಮೂದಿಸಿ: http://pmkisan-yojana-credit.org",
            "transliterated": "PM Kisan Yojana: Nimma bank account ge Rs 6,000 hana jama aagalu bank details verify maadi: http://pmkisan-yojana-credit.org",
            "codemixed": "PM Kisan Yojana hana Rs 6000 release aagide. Nimma account number enter madi receive madikolli: http://pmkisan-yojana-credit.org",
        },
        {
            "group_id": "PHISH_REW_03",
            "category": "fake_reward_lottery",
            "label": 1,
            "has_url": True,
            "english": "Flipkart Rewards: You have unredeemed shopping gift card worth Rs 10,000 expiring today. Redeem here: http://flipkart-scratch-win.in",
            "native_kannada": "ಫ್ಲಿಪ್‌ಕಾರ್ಟ್ ರಿವಾರ್ಡ್ಸ್: ನಿಮ್ಮ ರೂ 10,000 ಶಾಪಿಂಗ್ ಗಿಫ್ಟ್ ಕಾರ್ಡ್ ಇಂದು ಅವಧಿ ಮುಗಿಯಲಿದೆ. ತಕ್ಷಣ ರಿಡೀಮ್ ಮಾಡಿ: http://flipkart-scratch-win.in",
            "transliterated": "Flipkart Rewards: Nimma Rs 10,000 shopping gift card ivatte expire agatte. Redeem maadi: http://flipkart-scratch-win.in",
            "codemixed": "Flipkart offer: Rs 10000 gift voucher expire agtide today! Redeem madi click here: http://flipkart-scratch-win.in",
        },
        {
            "group_id": "PHISH_REW_04",
            "category": "fake_reward_lottery",
            "label": 1,
            "has_url": True,
            "english": "Gruha Lakshmi Scheme: Karnataka Govt has approved Rs 2,000 monthly allowance for your Aadhaar card. Collect at http://gruhalakshmi-gov-karnataka.org",
            "native_kannada": "ಗೃಹಲಕ್ಷ್ಮಿ ಯೋಜನೆ: ನಿಮ್ಮ ಆಧಾರ್ ಕಾರ್ಡ್‌ಗೆ ಕರ್ನಾಟಕ ಸರ್ಕಾರ ರೂ 2,000 ಮಾಸಿಕ ಭತ್ಯೆ ಅನುಮೋದಿಸಿದೆ. ಹಣ ಪಡೆಯಲು ಕ್ಲಿಕ್ ಮಾಡಿ: http://gruhalakshmi-gov-karnataka.org",
            "transliterated": "Gruha Lakshmi Yojana: Nimma Aadhaar card ge Karnataka sarkar Rs 2,000 approve madide. Hana padayalu click madi: http://gruhalakshmi-gov-karnataka.org",
            "codemixed": "Gruha Lakshmi scheme Rs 2000 allowance approve aagide. Verify account details in this portal: http://gruhalakshmi-gov-karnataka.org",
        },
        {
            "group_id": "PHISH_REW_05",
            "category": "fake_reward_lottery",
            "label": 1,
            "has_url": True,
            "english": "Jio 5G Bonus: Recharge free 84 days 5G pack + Rs 500 cashback for Indian independence day: http://jio-free-5g-bonus.xyz",
            "native_kannada": "ಜಿಯೋ 5G ಬೋನಸ್: ಸ್ವಾತಂತ್ರ್ಯ ದಿನಾಚರಣೆಗಾಗಿ ಉಚಿತ 84 ದಿನಗಳ 5G ಪ್ಯಾಕ್ ಮತ್ತು ರೂ 500 ಕ್ಯಾಶ್‌ಬ್ಯಾಕ್ ಪಡೆಯಿರಿ: http://jio-free-5g-bonus.xyz",
            "transliterated": "Jio 5G Bonus: Free 84 days 5G pack matthu Rs 500 cashback padayiri: http://jio-free-5g-bonus.xyz",
            "codemixed": "Jio special offer: Free 84 days 5G unlimited recharge activate madi eega: http://jio-free-5g-bonus.xyz",
        },

        # ==========================================
        # PHISHING: Job Scams, Delivery & Credential Harvesting (17-20)
        # ==========================================
        {
            "group_id": "PHISH_JOB_01",
            "category": "job_scam",
            "label": 1,
            "has_url": True,
            "english": "Part time work from home opportunity. Earn Rs 2,500 to Rs 8,000 daily by liking YouTube videos. Join our Telegram: http://t.me/kannada_daily_jobs",
            "native_kannada": "ಮನೆಯಿಂದಲೇ ಪಾರ್ಟ್ ಟೈಮ್ ಕೆಲಸ ಮಾಡುವ ಅವಕಾಶ. ಯೂಟ್ಯೂಬ್ ವೀಡಿಯೊ ಲೈಕ್ ಮಾಡಿ ದಿನಕ್ಕೆ ರೂ 2,500 ರಿಂದ ರೂ 8,000 ಗಳಿಸಿ. ಟೆಲಿಗ್ರಾಮ್ ಸೇರಿ: http://t.me/kannada_daily_jobs",
            "transliterated": "Maneyindale part time kelasa madi dinakke Rs 2500 inda 8000 galisi. Telegram join agi: http://t.me/kannada_daily_jobs",
            "codemixed": "Part time work from home! Daily Rs 5000 earn madi just simple tasks madi. Contact on Telegram: http://t.me/kannada_daily_jobs",
        },
        {
            "group_id": "PHISH_JOB_02",
            "category": "job_scam",
            "label": 1,
            "has_url": True,
            "english": "Amazon Hiring: Urgent requirement for Kannada data entry operators. Salary Rs 45,000/month. Register at http://amazon-india-jobs.xyz",
            "native_kannada": "ಅಮೆಜಾನ್ ನೇಮಕಾತಿ: ಕನ್ನಡ ಡೇಟಾ ಎಂಟ್ರಿ ಆಪರೇಟರ್‌ಗಳ ತುರ್ತು ಅಗತ್ಯವಿದೆ. ಮಾಸಿಕ ವೇತನ ರೂ 45,000. ನೋಂದಾಯಿಸಿ: http://amazon-india-jobs.xyz",
            "transliterated": "Amazon Nemakati: Kannada data entry kelasa iddare Rs 45,000 salary. Eegale register aagi: http://amazon-india-jobs.xyz",
            "codemixed": "Amazon Kannada data entry jobs available. Work from home salary Rs 45000. Apply fast: http://amazon-india-jobs.xyz",
        },
        {
            "group_id": "PHISH_DELIV_01",
            "category": "delivery_scam",
            "label": 1,
            "has_url": True,
            "english": "India Post: Your package #IN849204 cannot be delivered due to missing house number. Update your address within 12 hours: http://indiapost-parcel-update.com",
            "native_kannada": "ಇಂಡಿಯಾ ಪೋಸ್ಟ್: ವಿಳಾಸ ಅಪೂರ್ಣವಾಗಿರುವುದರಿಂದ ನಿಮ್ಮ ಪಾರ್ಸಲ್ #IN849204 ತಲುಪಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. 12 ಗಂಟೆಗಳಲ್ಲಿ ವಿಳಾಸ ನವೀಕರಿಸಿ: http://indiapost-parcel-update.com",
            "transliterated": "India Post: Vilasa thappagiruvudarinda nimma parcel delivery aagilla. 12 ghanteyalli address update maadi: http://indiapost-parcel-update.com",
            "codemixed": "India Post parcel deliver agilla address incomplete aagide. Update madoke link click madi: http://indiapost-parcel-update.com",
        },
        {
            "group_id": "PHISH_TAX_01",
            "category": "credential_harvesting",
            "label": 1,
            "has_url": True,
            "english": "Income Tax Department: Tax refund of Rs 18,450 approved for your PAN. Verify bank account number to credit: http://incometax-refund-gov.in",
            "native_kannada": "ಆದಾಯ ತೆರಿಗೆ ಇಲಾಖೆ: ನಿಮ್ಮ ಪಾನ್‌ಗೆ ರೂ 18,450 ತೆರಿಗೆ ಮರುಪಾವತಿ ಅನುಮೋದಿಸಲಾಗಿದೆ. ಹಣ ಪಡೆಯಲು ಬ್ಯಾಂಕ್ ಖಾತೆ ಪರಿಶೀಲಿಸಿ: http://incometax-refund-gov.in",
            "transliterated": "Income Tax Ilakhe: Nimma PAN ge Rs 18,450 tax refund approve aagide. Bank account verify maadi: http://incometax-refund-gov.in",
            "codemixed": "Income Tax Department refund Rs 18450 release aagide. Nimma account ge credit agbekandre verify madi: http://incometax-refund-gov.in",
        },

        # ==========================================
        # LEGITIMATE: Banking & Transaction OTPs (21-25)
        # ==========================================
        {
            "group_id": "LEGIT_OTP_01",
            "category": "legitimate_otp",
            "label": 0,
            "has_url": False,
            "english": "739281 is your OTP for SBI net banking login. Valid for 5 minutes. Never share this OTP with anyone, including bank staff.",
            "native_kannada": "739281 ನಿಮ್ಮ SBI ನೆಟ್ ಬ್ಯಾಂಕಿಂಗ್ ಲಾಗಿನ್ OTP ಆಗಿದೆ. 5 ನಿಮಿಷಗಳವರೆಗೆ ಮಾನ್ಯವಾಗಿರುತ್ತದೆ. ಬ್ಯಾಂಕ್ ಅಧಿಕಾರಿಗಳು ಸೇರಿದಂತೆ ಯಾರಿಗೂ OTP ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.",
            "transliterated": "739281 nimma SBI net banking login OTP. 5 nimisha valid ide. Yarigoo OTP share madbedi.",
            "codemixed": "739281 is your secret OTP for SBI login. 5 mins validity. Yarigoo share madbeda even bank officials.",
        },
        {
            "group_id": "LEGIT_OTP_02",
            "category": "legitimate_otp",
            "label": 0,
            "has_url": False,
            "english": "Your OTP for transaction of Rs 1,200 at Swiggy using HDFC Card ending 4091 is 849201. Do not share OTP for your security.",
            "native_kannada": "ಸ್ವಿಗ್ಗಿಯಲ್ಲಿ ನಿಮ್ಮ HDFC ಕಾರ್ಡ್ 4091 ಬಳಸಿ ರೂ 1,200 ವಹಿವಾಟಿಗೆ OTP 849201 ಆಗಿದೆ. ಸುರಕ್ಷತೆಗಾಗಿ ಯಾರಿಗೂ ತಿಳಿಸಬೇಡಿ.",
            "transliterated": "Swiggy alli HDFC card 4091 inda Rs 1200 payment ge OTP 849201 aagide. Yarigu share madbedi.",
            "codemixed": "HDFC Card payment of Rs 1,200 at Swiggy ge OTP 849201. Do not share OTP with anyone.",
        },
        {
            "group_id": "LEGIT_OTP_03",
            "category": "legitimate_otp",
            "label": 0,
            "has_url": False,
            "english": "392019 is your verification code to log in to Amazon. Never share your Amazon password or OTP with anyone.",
            "native_kannada": "392019 ಅಮೆಜಾನ್ ಲಾಗಿನ್ ಮಾಡಲು ನಿಮ್ಮ ಪರಿಶೀಲನಾ ಕೋಡ್ ಆಗಿದೆ. ನಿಮ್ಮ ಅಮೆಜಾನ್ ಪಾಸ್‌ವರ್ಡ್ ಅಥವಾ OTP ಯಾರಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ.",
            "transliterated": "392019 Amazon login madalu verification code. Nimma password athava OTP yarigu kodbedi.",
            "codemixed": "Amazon login verification code is 392019. Please do not disclose OTP to anyone.",
        },
        {
            "group_id": "LEGIT_TXN_01",
            "category": "legitimate_transaction",
            "label": 0,
            "has_url": False,
            "english": "Dear customer, Rs 35,000 credited to your Canara Bank A/c ending 8219 on 25-Aug-2026 by Salary NEFT. Total Avail Bal: Rs 42,150.",
            "native_kannada": "ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ ಕೆನರಾ ಬ್ಯಾಂಕ್ ಖಾತೆ 8219 ಕ್ಕೆ 25-ಆಗಸ್ಟ್-2026 ರಂದು ವೇತನವಾಗಿ ರೂ 35,000 ಜಮೆಯಾಗಿದೆ. ಲಭ್ಯವಿರುವ ಒಟ್ಟು ಬ್ಯಾಲೆನ್ಸ್: ರೂ 42,150.",
            "transliterated": "Grahakare, nimma Canara Bank khate 8219 ge salary Rs 35,000 credit aagide. Total Balance: Rs 42,150.",
            "codemixed": "Dear customer, Rs 35000 salary credit aytu nimma Canara Bank account ge. Available balance Rs 42,150.",
        },
        {
            "group_id": "LEGIT_TXN_02",
            "category": "legitimate_transaction",
            "label": 0,
            "has_url": False,
            "english": "UPI Alert: Rs 250 paid successfully to Nandini Milk Parlour from GPay UPI Ref 92839104819. Clear balance in your account.",
            "native_kannada": "UPI ಎಚ್ಚರಿಕೆ: ನಂದಿನಿ ಮಿಲ್ಕ್ ಪಾರ್ಲರ್‌ಗೆ ರೂ 250 ಯಶಸ್ವಿಯಾಗಿ ಪಾವತಿಸಲಾಗಿದೆ. UPI ರೆಫರೆನ್ಸ್ 92839104819.",
            "transliterated": "UPI Alert: Nandini Milk Parlour ge Rs 250 successfully pay aagide. UPI Ref 92839104819.",
            "codemixed": "Rs 250 paid to Nandini Milk Parlour via UPI. Transaction successful aagide. Ref: 92839104819.",
        },
        {
            "group_id": "LEGIT_TXN_03",
            "category": "legitimate_transaction",
            "label": 0,
            "has_url": False,
            "english": "SBI Alert: Rs 2,000 withdrawn from ATM at MG Road Bengaluru from A/c ending 1920. Avail Bal: Rs 15,400.",
            "native_kannada": "SBI ಎಚ್ಚರಿಕೆ: ಖಾತೆ 1920 ರಿಂದ ಬೆಂಗಳೂರಿನ ಎಂಜಿ ರಸ್ತೆಯ ಎಟಿಎಂನಲ್ಲಿ ರೂ 2,000 ಹಿಂಪಡೆಯಲಾಗಿದೆ. ಲಭ್ಯವಿರುವ ಬ್ಯಾಲೆನ್ಸ್: ರೂ 15,400.",
            "transliterated": "SBI Alert: Khate 1920 inda Bengaluru MG Road ATM nalli Rs 2,000 withdraw madalagide. Balance: Rs 15,400.",
            "codemixed": "SBI Alert: Rs 2000 cash withdraw aytu from MG Road ATM. Remaining balance Rs 15,400.",
        },

        # ==========================================
        # LEGITIMATE: Official Service Notifications & Receipts (26-30)
        # ==========================================
        {
            "group_id": "LEGIT_SERV_01",
            "category": "legitimate_service",
            "label": 0,
            "has_url": False,
            "english": "BESCOM: Payment of Rs 1,120 received successfully for Account ID 892019482. Thank you for paying on time.",
            "native_kannada": "ಬೆಸ್ಕಾಂ: ಖಾತೆ ಸಂಖ್ಯೆ 892019482 ಕ್ಕೆ ರೂ 1,120 ಪಾವತಿ ಯಶಸ್ವಿಯಾಗಿ ಸ್ವೀಕರಿಸಲಾಗಿದೆ. ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ ಪಾವತಿಸಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು.",
            "transliterated": "BESCOM: Khate sankhye 892019482 ge Rs 1,120 payment sweekarisalayitu. Dhanyavadagalu.",
            "codemixed": "BESCOM: Electricity bill payment of Rs 1,120 received successfully. Samayakke pay madiddakke thanks.",
        },
        {
            "group_id": "LEGIT_SERV_02",
            "category": "legitimate_service",
            "label": 0,
            "has_url": False,
            "english": "Indane Gas: Booking confirmed for cylinder ref #IND89201. Expected delivery within 2 working days. Refill charge Rs 850.",
            "native_kannada": "ಇಂಡೇನ್ ಗ್ಯಾಸ್: ಸಿಲಿಂಡರ್ ಬುಕಿಂಗ್ #IND89201 ದೃಢೀಕರಿಸಲಾಗಿದೆ. 2 ದಿನಗಳಲ್ಲಿ ವಿತರಣೆಯಾಗಲಿದೆ. ರೀಫಿಲ್ ಶುಲ್ಕ ರೂ 850.",
            "transliterated": "Indane Gas: Cylinder booking #IND89201 confirm aagide. 2 dinadalli delivery aagatte. Charge Rs 850.",
            "codemixed": "Indane Gas booking confirm aagide. 2 working days alli deliver agatte. Delivery charge Rs 850.",
        },
        {
            "group_id": "LEGIT_SERV_03",
            "category": "legitimate_service",
            "label": 0,
            "has_url": False,
            "english": "Airtel: Your unlimited prepaid pack of Rs 299 is successfully recharged. Valid for 28 days with 1.5GB/day data.",
            "native_kannada": "ಏರ್‌ಟೆಲ್: ನಿಮ್ಮ ರೂ 299 ರ ಪ್ರಿಪೇಯ್ಡ್ ಪ್ಯಾಕ್ ಯಶಸ್ವಿಯಾಗಿ ರೀಚಾರ್ಜ್ ಆಗಿದೆ. 28 ದಿನಗಳವರೆಗೆ 1.5GB/ದಿನ ಡೇಟಾ ಮಾನ್ಯವಾಗಿರುತ್ತದೆ.",
            "transliterated": "Airtel: Nimma Rs 299 recharge successfully aagide. 28 dina 1.5GB daily data sigatte.",
            "codemixed": "Airtel Rs 299 pack successfully recharge aaythu. 28 days validity with 1.5GB/day data.",
        },
        {
            "group_id": "LEGIT_SERV_04",
            "category": "legitimate_service",
            "label": 0,
            "has_url": False,
            "english": "KSRTC Booking: Your ticket from Bengaluru to Mangaluru on 28-Aug-2026 is confirmed. PNR: KSRTC892018. Seat 14.",
            "native_kannada": "KSRTC ಬುಕಿಂಗ್: 28-ಆಗಸ್ಟ್-2026 ರಂದು ಬೆಂಗಳೂರಿನಿಂದ ಮಂಗಳೂರಿಗೆ ನಿಮ್ಮ ಟಿಕೆಟ್ ದೃಢೀಕರಿಸಲಾಗಿದೆ. PNR: KSRTC892018. ಸೀಟ್ ಸಂಖ್ಯೆ 14.",
            "transliterated": "KSRTC Booking: Bengaluru inda Mangalurige nimma ticket confirm aagide. PNR: KSRTC892018. Seat 14.",
            "codemixed": "KSRTC bus ticket Bengaluru to Mangalore confirm aytu. PNR: KSRTC892018. Have a safe journey.",
        },
        {
            "group_id": "LEGIT_SERV_05",
            "category": "legitimate_service",
            "label": 0,
            "has_url": False,
            "english": "Apollo Pharmacy: Your medicine order #AP9201 is packed and ready for delivery. Total amount Rs 450.",
            "native_kannada": "ಅಪೊಲೊ ಫಾರ್ಮಸಿ: ನಿಮ್ಮ ಔಷಧಿ ಆರ್ಡರ್ #AP9201 ಪ್ಯಾಕ್ ಮಾಡಲಾಗಿದೆ ಮತ್ತು ವಿತರಣೆಗೆ ಸಿದ್ಧವಾಗಿದೆ. ಒಟ್ಟು ಮೊತ್ತ ರೂ 450.",
            "transliterated": "Apollo Pharmacy: Nimma medicine order #AP9201 pack aagide. Delivery ready ide. Amount Rs 450.",
            "codemixed": "Apollo Pharmacy: Medicine order #AP9201 is ready for delivery. Amount Rs 450 COD.",
        },

        # ==========================================
        # LEGITIMATE: Personal & Casual Conversations (31-35)
        # ==========================================
        {
            "group_id": "LEGIT_PERS_01",
            "category": "legitimate_personal",
            "label": 0,
            "has_url": False,
            "english": "Hi Ramesh, are you coming to Mysore this weekend for the festival? Let me know the train timing.",
            "native_kannada": "ನಮಸ್ಕಾರ ರಮೇಶ್, ಈ ವಾರಾಂತ್ಯದಲ್ಲಿ ಹಬ್ಬಕ್ಕಾಗಿ ಮೈಸೂರಿಗೆ ಬರುತ್ತಿದ್ದೀರಾ? ರೈಲಿನ ಸಮಯ ತಿಳಿಸಿ.",
            "transliterated": "Namaskara Ramesh, ee weekend habbakke Mysurige bartheera? Train timing heli.",
            "codemixed": "Hey Ramesh, ee weekend Mysore ge barta idira festival ge? Train timing send madi please.",
        },
        {
            "group_id": "LEGIT_PERS_02",
            "category": "legitimate_personal",
            "label": 0,
            "has_url": False,
            "english": "Good morning! The team meeting is rescheduled to 4:00 PM today in Conference Room B.",
            "native_kannada": "ಶುಭೋದಯ! ಇಂದಿನ ತಂಡದ ಸಭೆಯನ್ನು ಸಂಜೆ 4:00 ಕ್ಕೆ ಕಾನ್ಫರೆನ್ಸ್ ಕೊಠಡಿ B ನಲ್ಲಿ ಮರುಹೊಂದಿಸಲಾಗಿದೆ.",
            "transliterated": "Shubhoday! Ivattina team meeting sanje 4:00 PM ge Conference Room B nalli reschedule aagide.",
            "codemixed": "Good morning! Ivattu meeting 4:00 PM ge shift aagide in Conference Room B.",
        },
        {
            "group_id": "LEGIT_PERS_03",
            "category": "legitimate_personal",
            "label": 0,
            "has_url": False,
            "english": "Happy Ugadi to you and your family! May this new year bring happiness, health, and prosperity.",
            "native_kannada": "ನಿಮಗೂ ಮತ್ತು ನಿಮ್ಮ ಕುಟುಂಬಕ್ಕೂ ಯುಗಾದಿ ಹಬ್ಬದ ಹಾರ್ದಿಕ ಶುಭಾಶಯಗಳು! ಈ ಹೊಸ ವರ್ಷವು ಸಂತೋಷ ಮತ್ತು ಸಮೃದ್ಧಿಯನ್ನು ತರಲಿ.",
            "transliterated": "Nimagoo matthu nimma kutumbakkoo Yugadi habbada shubhashayagalu! Ee hosa varsha santhosha tharali.",
            "codemixed": "Happy Ugadi to you and family! Habbada hardika shubhashayagalu, have a great year ahead.",
        },
        {
            "group_id": "LEGIT_PERS_04",
            "category": "legitimate_personal",
            "label": 0,
            "has_url": False,
            "english": "I have shared the project presentation document over email. Please review and share your feedback.",
            "native_kannada": "ನಾನು ಯೋಜನೆಯ ಪ್ರಸ್ತುತಿ ದಾಖಲೆಯನ್ನು ಇಮೇಲ್ ಮೂಲಕ ಹಂಚಿಕೊಂಡಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ಪರಿಶೀಲಿಸಿ ನಿಮ್ಮ ಅಭಿಪ್ರಾಯ ತಿಳಿಸಿ.",
            "transliterated": "Nanu project presentation document email alli share madiddini. Review madi feedback thilisi.",
            "codemixed": "Project presentation document email kalsidini. Please nodi feedback share madi.",
        },
        {
            "group_id": "LEGIT_PERS_05",
            "category": "legitimate_personal",
            "label": 0,
            "has_url": False,
            "english": "Did you reach Bangalore safely? Call me when you are free.",
            "native_kannada": "ಬೆಂಗಳೂರನ್ನು ಸುರಕ್ಷಿತವಾಗಿ ತಲುಪಿದಿರಾ? ಬಿಡುವಾದಾಗ ನನಗೆ ಕರೆ ಮಾಡಿ.",
            "transliterated": "Bangalore ge safe aagi thalupidira? Free aadaga nange call maadi.",
            "codemixed": "Bangalore reach aagidira safely? Free aagi call madi mathadana.",
        },
    ]

    return templates


def expand_dataset(templates: List[Dict]) -> pd.DataFrame:
    """Expands base templates into individual records across languages and scripts."""
    records = []

    for item in templates:
        group_id = item["group_id"]
        category = item["category"]
        label = item["label"]
        has_url = item["has_url"]

        # English variant
        records.append({
            "group_id": group_id,
            "text": item["english"],
            "label": label,
            "language": "english",
            "script": "latin",
            "category": category,
            "has_url": has_url,
            "variant_type": "original_english",
        })

        # Native Kannada translation
        records.append({
            "group_id": group_id,
            "text": item["native_kannada"],
            "label": label,
            "language": "kannada",
            "script": "kannada",
            "category": category,
            "has_url": has_url,
            "variant_type": "native_kannada_translation",
        })

        # Transliterated Kannada (Kanglish)
        records.append({
            "group_id": group_id,
            "text": item["transliterated"],
            "label": label,
            "language": "kannada",
            "script": "latin",
            "category": category,
            "has_url": has_url,
            "variant_type": "transliterated_kannada",
        })

        # Code-mixed Kannada-English
        records.append({
            "group_id": group_id,
            "text": item["codemixed"],
            "label": label,
            "language": "code-mixed",
            "script": "latin",
            "category": category,
            "has_url": has_url,
            "variant_type": "code_mixed",
        })

    df = pd.DataFrame(records)
    return df


def perform_group_split(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Splits dataset strictly by group_id to prevent any data leakage.
    
    Guarantees that no message and its translated/transliterated variants span across
    Train, Validation, or Test splits.
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Ratios must sum to 1.0"

    np.random.seed(random_seed)

    # Get unique group IDs separated by label for stratified group split
    phish_groups = df[df["label"] == 1]["group_id"].unique()
    legit_groups = df[df["label"] == 0]["group_id"].unique()

    np.random.shuffle(phish_groups)
    np.random.shuffle(legit_groups)

    def split_group_list(groups):
        n = len(groups)
        n_train = int(round(n * train_ratio))
        n_val = int(round(n * val_ratio))
        train_g = groups[:n_train]
        val_g = groups[n_train:n_train + n_val]
        test_g = groups[n_train + n_val:]
        return set(train_g), set(val_g), set(test_g)

    p_train, p_val, p_test = split_group_list(phish_groups)
    l_train, l_val, l_test = split_group_list(legit_groups)

    train_groups = p_train | l_train
    val_groups = p_val | l_val
    test_groups = p_test | l_test

    # Strictly verify zero group overlap
    assert len(train_groups & val_groups) == 0, "Group leakage detected between Train and Validation!"
    assert len(train_groups & test_groups) == 0, "Group leakage detected between Train and Test!"
    assert len(val_groups & test_groups) == 0, "Group leakage detected between Validation and Test!"

    train_df = df[df["group_id"].isin(train_groups)].copy().reset_index(drop=True)
    val_df = df[df["group_id"].isin(val_groups)].copy().reset_index(drop=True)
    test_df = df[df["group_id"].isin(test_groups)].copy().reset_index(drop=True)

    return train_df, val_df, test_df


def extract_specialized_test_subsets(test_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Extracts specialized evaluation test subsets as required by testing-and-evaluation.md."""
    subsets = {
        "test_native_kannada": test_df[test_df["variant_type"] == "native_kannada_translation"].copy().reset_index(drop=True),
        "test_transliterated_kannada": test_df[test_df["variant_type"] == "transliterated_kannada"].copy().reset_index(drop=True),
        "test_codemixed": test_df[test_df["variant_type"] == "code_mixed"].copy().reset_index(drop=True),
        "test_english": test_df[test_df["variant_type"] == "original_english"].copy().reset_index(drop=True),
    }
    return subsets


def curate_and_export_all() -> Dict:
    """Main curation pipeline: builds, splits, and saves datasets and summary stats."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    SUBSETS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate full dataset from templates
    templates = get_base_message_templates()
    full_df = expand_dataset(templates)

    # Export raw dataset
    raw_path = RAW_DATA_DIR / "raksha_full_dataset.csv"
    full_df.to_csv(raw_path, index=False, encoding="utf-8")

    # 2. Perform strictly group-based split (70 / 15 / 15)
    train_df, val_df, test_df = perform_group_split(full_df, 0.70, 0.15, 0.15, random_seed=42)

    # Export processed splits
    train_df.to_csv(PROCESSED_DATA_DIR / "train.csv", index=False, encoding="utf-8")
    val_df.to_csv(PROCESSED_DATA_DIR / "validation.csv", index=False, encoding="utf-8")
    test_df.to_csv(PROCESSED_DATA_DIR / "test.csv", index=False, encoding="utf-8")

    # 3. Extract and export specialized test subsets
    subsets = extract_specialized_test_subsets(test_df)
    for name, s_df in subsets.items():
        s_df.to_csv(SUBSETS_DIR / f"{name}.csv", index=False, encoding="utf-8")

    # 4. Generate summary report
    summary = {
        "total_groups": len(templates),
        "total_samples": len(full_df),
        "phishing_samples": int((full_df["label"] == 1).sum()),
        "legitimate_samples": int((full_df["label"] == 0).sum()),
        "splits": {
            "train": {
                "samples": len(train_df),
                "groups": int(train_df["group_id"].nunique()),
                "phishing": int((train_df["label"] == 1).sum()),
                "legitimate": int((train_df["label"] == 0).sum()),
                "ratio": round(len(train_df) / len(full_df), 4),
            },
            "validation": {
                "samples": len(val_df),
                "groups": int(val_df["group_id"].nunique()),
                "phishing": int((val_df["label"] == 1).sum()),
                "legitimate": int((val_df["label"] == 0).sum()),
                "ratio": round(len(val_df) / len(full_df), 4),
            },
            "test": {
                "samples": len(test_df),
                "groups": int(test_df["group_id"].nunique()),
                "phishing": int((test_df["label"] == 1).sum()),
                "legitimate": int((test_df["label"] == 0).sum()),
                "ratio": round(len(test_df) / len(full_df), 4),
            },
        },
        "language_distribution": full_df["language"].value_counts().to_dict(),
        "specialized_test_subsets": {name: len(s_df) for name, s_df in subsets.items()},
        "group_leakage": {
            "train_val_overlap": len(set(train_df["group_id"]) & set(val_df["group_id"])),
            "train_test_overlap": len(set(train_df["group_id"]) & set(test_df["group_id"])),
            "val_test_overlap": len(set(val_df["group_id"]) & set(test_df["group_id"])),
        },
    }

    with open(PROCESSED_DATA_DIR / "dataset_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return summary


if __name__ == "__main__":
    summary = curate_and_export_all()
    print("Dataset curation completed successfully.")
    print(json.dumps(summary, indent=2))
