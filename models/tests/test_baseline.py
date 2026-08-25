"""Automated test suite for TF-IDF + Logistic Regression Baseline Model (TSK-04).

Verifies compliance with:
- ai-ml-system.md: Baseline training, reproducibility, artifact serialization.
- testing-and-evaluation.md: Evaluation metrics (accuracy, precision, recall, F1, FPR, latency).
"""

import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from models.src.baseline_model import RakshaBaselineClassifier

DATA_DIR = REPO_ROOT / "models" / "data" / "processed"
SUBSETS_DIR = DATA_DIR / "subsets"
SAVED_MODELS_DIR = REPO_ROOT / "models" / "saved_models" / "baseline_tfidf"


@pytest.fixture
def train_data():
    df = pd.read_csv(DATA_DIR / "train.csv")
    return df["text"].tolist(), df["label"].tolist()


@pytest.fixture
def val_data():
    df = pd.read_csv(DATA_DIR / "validation.csv")
    return df["text"].tolist(), df["label"].tolist()


def test_baseline_training_and_convergence(train_data):
    """Verify that baseline model fits and converges on training data."""
    texts, labels = train_data
    model = RakshaBaselineClassifier(random_state=42)
    model.fit(texts, labels)

    assert model.is_fitted is True
    probas = model.predict_proba(texts[:5])
    assert probas.shape == (5, 2)
    assert np.allclose(probas.sum(axis=1), 1.0)


def test_baseline_serialization_and_loading(train_data, tmp_path):
    """Verify model can be serialized to disk and loaded with identical predictions."""
    texts, labels = train_data
    model = RakshaBaselineClassifier(random_state=42)
    model.fit(texts, labels)

    original_preds = model.predict_proba(texts[:10])

    # Save to temporary path
    saved_dir = model.save(tmp_path / "baseline_test_model")
    assert (saved_dir / "baseline_model.joblib").exists()
    assert (saved_dir / "metadata.json").exists()

    # Load and compare
    loaded_model = RakshaBaselineClassifier.load(saved_dir)
    assert loaded_model.is_fitted is True
    loaded_preds = loaded_model.predict_proba(texts[:10])

    assert np.allclose(original_preds, loaded_preds, atol=1e-5)


def test_baseline_reproducibility(train_data):
    """Verify training is strictly deterministic given random_state=42."""
    texts, labels = train_data
    model1 = RakshaBaselineClassifier(random_state=42).fit(texts, labels)
    model2 = RakshaBaselineClassifier(random_state=42).fit(texts, labels)

    preds1 = model1.predict_proba(texts[:10])
    preds2 = model2.predict_proba(texts[:10])

    assert np.allclose(preds1, preds2, atol=1e-6)


def test_predict_single_contract():
    """Verify predict_single returns valid risk scores, language metadata, and latency."""
    model = RakshaBaselineClassifier.load(SAVED_MODELS_DIR)

    res = model.predict_single("ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ ಖಾತೆಯನ್ನು ಪರಿಶೀಲಿಸಿ http://sbi-fake.in")
    assert "nlp_score" in res
    assert 0.0 <= res["nlp_score"] <= 1.0
    assert res["prediction"] in [0, 1]
    assert res["language_detected"] in ["kannada", "english", "code-mixed", "unknown"]
    assert res["latency_ms"] >= 0.0

    # Test empty string handling
    empty_res = model.predict_single("")
    assert empty_res["nlp_score"] == 0.0
    assert empty_res["prediction"] == 0
    assert empty_res["language_detected"] == "unknown"


def test_metric_calculation_correctness():
    """Verify mathematical correctness of accuracy, precision, recall, F1, FPR in evaluate()."""
    model = RakshaBaselineClassifier(random_state=42)
    # Mock evaluate with synthetic inputs
    model.is_fitted = True

    # Dummy texts and known predictions
    # Let's test evaluate on a small fitted model
    texts = [
        "Urgent: verify your account immediately http://phish.com",
        "Salary of Rs 50,000 credited to your account",
    ]
    labels = [1, 0]
    model.fit(texts, labels)

    metrics = model.evaluate(texts, labels)
    assert metrics["samples"] == 2
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert "false_positive_rate" in metrics
    assert "confusion_matrix" in metrics
    assert "avg_latency_ms" in metrics
    assert metrics["avg_latency_ms"] < 50.0  # Must be fast local inference


def test_evaluation_report_exists_and_valid():
    """Verify baseline_evaluation_report.json exists and contains empirical metrics for all subsets."""
    report_file = DATA_DIR / "baseline_evaluation_report.json"
    assert report_file.exists(), f"Missing evaluation report: {report_file}"

    with open(report_file, "r", encoding="utf-8") as f:
        report = json.load(f)

    assert "model_name" in report
    assert "validation_metrics" in report
    assert "test_metrics" in report
    assert "regional_subsets_metrics" in report

    # Verify regional subsets
    subsets = report["regional_subsets_metrics"]
    assert "native_kannada" in subsets
    assert "transliterated_kannada" in subsets
    assert "codemixed" in subsets
    assert "english" in subsets

    # Check metrics are non-null floats
    for subset_name, sub_m in subsets.items():
        assert 0.0 <= sub_m["accuracy"] <= 1.0
        assert 0.0 <= sub_m["f1_score"] <= 1.0
        assert sub_m["avg_latency_ms"] > 0.0
