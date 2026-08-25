import json
import sys
from pathlib import Path
from typing import Dict

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from models.src.baseline_model import RakshaBaselineClassifier

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
SUBSETS_DIR = DATA_DIR / "subsets"
SAVED_MODELS_DIR = BASE_DIR / "saved_models" / "baseline_tfidf"


def run_baseline_training() -> Dict:
    """Executes the full baseline training and evaluation pipeline."""
    print("Loading datasets...")
    train_df = pd.read_csv(DATA_DIR / "train.csv")
    val_df = pd.read_csv(DATA_DIR / "validation.csv")
    test_df = pd.read_csv(DATA_DIR / "test.csv")

    # Load specialized evaluation subsets
    subsets = {
        "native_kannada": pd.read_csv(SUBSETS_DIR / "test_native_kannada.csv"),
        "transliterated_kannada": pd.read_csv(SUBSETS_DIR / "test_transliterated_kannada.csv"),
        "codemixed": pd.read_csv(SUBSETS_DIR / "test_codemixed.csv"),
        "english": pd.read_csv(SUBSETS_DIR / "test_english.csv"),
    }

    print(f"Training on {len(train_df)} samples...")
    model = RakshaBaselineClassifier(random_state=42)
    model.fit(train_df["text"].tolist(), train_df["label"].tolist())

    print("Evaluating on Validation set...")
    val_metrics = model.evaluate(val_df["text"].tolist(), val_df["label"].tolist())

    print("Evaluating on Held-Out Test set...")
    test_metrics = model.evaluate(test_df["text"].tolist(), test_df["label"].tolist())

    print("Evaluating on Specialized Regional Test Subsets...")
    subset_metrics = {}
    for name, s_df in subsets.items():
        subset_metrics[name] = model.evaluate(s_df["text"].tolist(), s_df["label"].tolist())

    # Save model artifact
    print(f"Saving baseline model to {SAVED_MODELS_DIR}...")
    model.save(SAVED_MODELS_DIR)

    report = {
        "model_name": "TF-IDF + Logistic Regression Baseline",
        "training_samples": len(train_df),
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
        "regional_subsets_metrics": subset_metrics,
    }

    report_path = DATA_DIR / "baseline_evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Evaluation report saved to {report_path}")
    return report


if __name__ == "__main__":
    report = run_baseline_training()
    print("\n--- BASELINE EVALUATION SUMMARY ---")
    print(json.dumps(report, indent=2))
