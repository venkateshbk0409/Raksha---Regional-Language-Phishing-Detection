"""Unit tests for Transformer Candidates Evaluation (TSK-08).

Verifies compliance with:
- ai-ml-system.md: Empirical evaluation of MuRIL and XLM-RoBERTa against TF-IDF baseline.
- testing-and-evaluation.md: Metric structure and leakage-free dataset utilization.
"""

import json
from pathlib import Path
import pytest
from models.src.evaluate_transformers import (
    REPORT_OUTPUT_PATH,
    TransformerFeatureClassifier,
    compute_metrics,
    run_transformer_evaluation,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "models" / "data" / "processed"


def test_compute_metrics_math():
    """Verify compute_metrics outputs exact mathematical precision and confusion matrix."""
    y_true = [1, 1, 0, 0]
    y_pred = [1, 0, 0, 1]
    latencies = [10.0, 20.0, 30.0, 40.0]

    metrics = compute_metrics(y_true, y_pred, latencies)
    assert metrics["accuracy"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1_score"] == 0.5
    assert metrics["false_positive_rate"] == 0.5
    assert metrics["avg_latency_ms"] == 25.0
    assert metrics["confusion_matrix"] == {
        "true_negative": 1,
        "false_positive": 1,
        "false_negative": 1,
        "true_positive": 1,
    }


def test_transformer_evaluation_report_artifact_structure():
    """Verify transformer evaluation report exists and contains all required candidates and splits."""
    assert REPORT_OUTPUT_PATH.exists(), "Transformer evaluation report JSON does not exist."

    with open(REPORT_OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "timestamp" in data
    assert "dataset_split_summary" in data
    assert data["dataset_split_summary"]["train_samples"] > 0
    assert data["dataset_split_summary"]["validation_samples"] > 0
    assert data["dataset_split_summary"]["test_samples"] > 0

    assert "candidates" in data
    assert "muril" in data["candidates"]
    assert "xlm_roberta" in data["candidates"]

    # Check MuRIL metrics
    muril = data["candidates"]["muril"]
    assert "validation_metrics" in muril
    assert "held_out_test_metrics" in muril
    assert "regional_subsets_metrics" in muril
    assert "avg_latency_ms" in muril["validation_metrics"]
    assert 0.0 <= muril["validation_metrics"]["f1_score"] <= 1.0

    # Check XLM-RoBERTa metrics
    xlm = data["candidates"]["xlm_roberta"]
    assert "validation_metrics" in xlm
    assert "held_out_test_metrics" in xlm
    assert "regional_subsets_metrics" in xlm

    # Check baseline comparison
    assert "baseline_tfidf_comparison" in data
    assert data["baseline_tfidf_comparison"]["model_name"] == "TF-IDF + Logistic Regression Baseline"


def test_transformer_classifier_deterministic_inference():
    """Verify TransformerFeatureClassifier predict produces reproducible probabilities."""
    clf = TransformerFeatureClassifier(model_name="mock-transformer", candidate_id="mock_id", random_state=42)
    texts = [
        "Dear customer, your bank OTP is 123456.",
        "URGENT: Your account is suspended. Verify at http://evil.com",
    ]
    labels = [0, 1]
    clf.fit(texts, labels)

    preds1, probs1, _ = clf.predict(texts)
    preds2, probs2, _ = clf.predict(texts)

    assert preds1 == preds2
    assert probs1 == probs2
