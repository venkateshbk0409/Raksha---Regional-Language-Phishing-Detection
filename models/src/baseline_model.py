"""TF-IDF + Logistic Regression Baseline Model for Raksha.

Conforms strictly to:
- ai-ml-system.md: Mandatory TF-IDF + Logistic Regression baseline, empirical metrics.
- testing-and-evaluation.md: Evaluation metrics (Precision, Recall, F1, FPR, Latency).
- feature-specification.md: FEAT-04 NLP classification track.
"""

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Ensure repository root is in sys.path for reliable imports
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, accuracy_score
from sklearn.pipeline import FeatureUnion, Pipeline

from models.src.preprocessor import TextPreprocessor, preprocessor


class RakshaBaselineClassifier:
    """Baseline phishing classifier combining subword/word TF-IDF and Logistic Regression."""

    def __init__(
        self,
        random_state: int = 42,
        c_param: float = 1.0,
        max_iter: int = 1000,
        class_weight: str = "balanced",
    ):
        self.random_state = random_state
        self.c_param = c_param
        self.max_iter = max_iter
        self.class_weight = class_weight
        self.preprocessor = preprocessor

        # Feature Union: Word n-grams + Character n-grams (subword level)
        # Captures lexical keywords as well as morphological suffixes in Kanglish/Kannada
        word_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=3000,
            sublinear_tf=True,
            token_pattern=r"(?u)\b\w+\b",
        )
        char_vectorizer = TfidfVectorizer(
            ngram_range=(3, 5),
            analyzer="char_wb",
            max_features=4000,
            sublinear_tf=True,
        )

        self.feature_extractor = FeatureUnion([
            ("word_tfidf", word_vectorizer),
            ("char_tfidf", char_vectorizer),
        ])

        self.classifier = LogisticRegression(
            C=self.c_param,
            max_iter=self.max_iter,
            random_state=self.random_state,
            class_weight=self.class_weight,
            solver="lbfgs",
        )

        self.pipeline: Optional[Pipeline] = Pipeline([
            ("features", self.feature_extractor),
            ("clf", self.classifier),
        ])
        self.is_fitted: bool = False

    def _preprocess_texts(self, texts: List[str]) -> List[str]:
        """Runs TextPreprocessor on texts and prepares normalized representations."""
        processed = []
        for text in texts:
            prep_res = self.preprocessor.preprocess(text)
            # Use normalized tokens joined into string for vocabulary consolidation
            token_str = " ".join(prep_res.normalized_tokens) if prep_res.normalized_tokens else prep_res.cleaned_text
            processed.append(token_str)
        return processed

    def fit(self, texts: List[str], labels: Union[List[int], np.ndarray]) -> "RakshaBaselineClassifier":
        """Fits the TF-IDF feature union and Logistic Regression classifier."""
        processed_texts = self._preprocess_texts(texts)
        y = np.array(labels, dtype=int)

        self.pipeline.fit(processed_texts, y)
        self.is_fitted = True
        return self

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Predicts class probabilities [p(legitimate), p(phishing)]."""
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted. Call fit() or load() before predict.")
        processed_texts = self._preprocess_texts(texts)
        return self.pipeline.predict_proba(processed_texts)

    def predict(self, texts: List[str]) -> np.ndarray:
        """Predicts binary class labels (0 = Legitimate, 1 = Phishing)."""
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted. Call fit() or load() before predict.")
        processed_texts = self._preprocess_texts(texts)
        return self.pipeline.predict(processed_texts)

    def predict_single(self, text: str) -> Dict[str, Any]:
        """Predicts phishing risk score and language metadata for a single string."""
        start_time = time.perf_counter()
        prep_res = self.preprocessor.preprocess(text)

        if prep_res.is_empty:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "nlp_score": 0.0,
                "prediction": 0,
                "language_detected": "unknown",
                "script": "unknown",
                "latency_ms": round(latency_ms, 3),
            }

        token_str = " ".join(prep_res.normalized_tokens) if prep_res.normalized_tokens else prep_res.cleaned_text
        proba = self.pipeline.predict_proba([token_str])[0]
        phishing_prob = float(proba[1])
        prediction = 1 if phishing_prob >= 0.50 else 0

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "nlp_score": round(phishing_prob, 4),
            "prediction": prediction,
            "language_detected": prep_res.language,
            "script": prep_res.script,
            "latency_ms": round(latency_ms, 3),
        }

    def evaluate(self, texts: List[str], labels: Union[List[int], np.ndarray]) -> Dict[str, Any]:
        """Computes comprehensive empirical metrics required by testing-and-evaluation.md."""
        y_true = np.array(labels, dtype=int)

        start_time = time.perf_counter()
        probas = self.predict_proba(texts)
        end_time = time.perf_counter()

        total_time_ms = (end_time - start_time) * 1000.0
        avg_latency_ms = total_time_ms / max(1, len(texts))

        y_pred = (probas[:, 1] >= 0.50).astype(int)

        accuracy = float(accuracy_score(y_true, y_pred))
        precision = float(precision_score(y_true, y_pred, zero_division=0))
        recall = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        # Confusion Matrix: [[TN, FP], [FN, TP]]
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

        # False-Positive Rate on benign samples: FP / (FP + TN)
        benign_total = fp + tn
        fpr = float(fp / benign_total) if benign_total > 0 else 0.0

        return {
            "samples": len(texts),
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "false_positive_rate": round(fpr, 4),
            "confusion_matrix": {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
            },
            "avg_latency_ms": round(avg_latency_ms, 3),
            "total_latency_ms": round(total_time_ms, 3),
        }

    def save(self, model_dir: Union[str, Path]) -> Path:
        """Serializes pipeline and metadata to disk."""
        target_dir = Path(model_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        model_path = target_dir / "baseline_model.joblib"
        joblib.dump(self.pipeline, model_path)

        metadata = {
            "model_type": "TF-IDF + Logistic Regression",
            "random_state": self.random_state,
            "c_param": self.c_param,
            "max_iter": self.max_iter,
            "class_weight": self.class_weight,
            "is_fitted": self.is_fitted,
        }
        with open(target_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return target_dir

    @classmethod
    def load(cls, model_dir: Union[str, Path]) -> "RakshaBaselineClassifier":
        """Loads serialized pipeline and restores classifier instance."""
        target_dir = Path(model_dir)
        model_path = target_dir / "baseline_model.joblib"
        meta_path = target_dir / "metadata.json"

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        instance = cls()
        instance.pipeline = joblib.load(model_path)
        instance.is_fitted = True

        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                instance.random_state = meta.get("random_state", 42)
                instance.c_param = meta.get("c_param", 1.0)
                instance.max_iter = meta.get("max_iter", 1000)

        return instance
