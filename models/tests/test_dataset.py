"""Automated test suite verifying dataset integrity, 0% leakage, and split ratios for TSK-02."""

import json
from pathlib import Path
import pandas as pd
import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SUBSETS_DIR = PROCESSED_DATA_DIR / "subsets"


def test_dataset_files_exist():
    """Verify all raw, processed, and subset files are generated."""
    expected_files = [
        RAW_DATA_DIR / "raksha_full_dataset.csv",
        PROCESSED_DATA_DIR / "train.csv",
        PROCESSED_DATA_DIR / "validation.csv",
        PROCESSED_DATA_DIR / "test.csv",
        PROCESSED_DATA_DIR / "dataset_summary.json",
        SUBSETS_DIR / "test_native_kannada.csv",
        SUBSETS_DIR / "test_transliterated_kannada.csv",
        SUBSETS_DIR / "test_codemixed.csv",
        SUBSETS_DIR / "test_english.csv",
    ]
    for file_path in expected_files:
        assert file_path.exists(), f"Missing expected dataset file: {file_path}"


def test_zero_group_leakage():
    """Verify strictly 0% group leakage across Train, Validation, and Test splits.
    
    A translated or augmented variant and its corresponding original source text
    MUST NOT span across Train, Validation, and Test splits per ai-ml-system.md.
    """
    train_df = pd.read_csv(PROCESSED_DATA_DIR / "train.csv")
    val_df = pd.read_csv(PROCESSED_DATA_DIR / "validation.csv")
    test_df = pd.read_csv(PROCESSED_DATA_DIR / "test.csv")

    train_groups = set(train_df["group_id"].unique())
    val_groups = set(val_df["group_id"].unique())
    test_groups = set(test_df["group_id"].unique())

    # Assert mutual exclusivity
    assert len(train_groups & val_groups) == 0, f"Leakage detected between Train and Val: {train_groups & val_groups}"
    assert len(train_groups & test_groups) == 0, f"Leakage detected between Train and Test: {train_groups & test_groups}"
    assert len(val_groups & test_groups) == 0, f"Leakage detected between Val and Test: {val_groups & test_groups}"


def test_split_proportions():
    """Verify that dataset splits match approximately 70% Train, 15% Val, 15% Test."""
    with open(PROCESSED_DATA_DIR / "dataset_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    train_ratio = summary["splits"]["train"]["ratio"]
    val_ratio = summary["splits"]["validation"]["ratio"]
    test_ratio = summary["splits"]["test"]["ratio"]

    # Ratios within expected tolerance
    assert 0.65 <= train_ratio <= 0.75, f"Unexpected train ratio: {train_ratio}"
    assert 0.10 <= val_ratio <= 0.20, f"Unexpected val ratio: {val_ratio}"
    assert 0.10 <= test_ratio <= 0.20, f"Unexpected test ratio: {test_ratio}"
    assert round(train_ratio + val_ratio + test_ratio, 2) == 1.0


def test_data_schema_and_integrity():
    """Verify columns, non-null values, length constraints, and valid labels."""
    required_cols = {
        "group_id", "text", "label", "language", "script", "category", "has_url", "variant_type"
    }

    for split_name in ["train.csv", "validation.csv", "test.csv"]:
        df = pd.read_csv(PROCESSED_DATA_DIR / split_name)
        assert required_cols.issubset(df.columns), f"Missing required columns in {split_name}"

        # No nulls or empty texts
        assert df["text"].isnull().sum() == 0, f"Null texts found in {split_name}"
        assert (df["text"].str.strip() == "").sum() == 0, f"Empty texts found in {split_name}"

        # Length constraints (1 to 2000 characters)
        assert (df["text"].str.len() > 2000).sum() == 0, f"Texts > 2000 chars found in {split_name}"
        assert (df["text"].str.len() < 1).sum() == 0, f"Texts < 1 char found in {split_name}"

        # Labels strictly 0 or 1
        assert set(df["label"].unique()).issubset({0, 1}), f"Invalid label values in {split_name}"

        # Both classes present in all splits
        assert 0 in df["label"].values, f"No legitimate samples in {split_name}"
        assert 1 in df["label"].values, f"No phishing samples in {split_name}"


def test_specialized_evaluation_subsets():
    """Verify all 4 specialized regional evaluation subsets are valid and non-empty."""
    subsets = [
        ("test_native_kannada.csv", "kannada", "kannada"),
        ("test_english.csv", "english", "latin"),
        ("test_transliterated_kannada.csv", "kannada", "latin"),
        ("test_codemixed.csv", "code-mixed", "latin"),
    ]

    for filename, expected_lang, expected_script in subsets:
        df = pd.read_csv(SUBSETS_DIR / filename)
        assert len(df) > 0, f"Subset {filename} is empty"
        assert (df["language"] == expected_lang).all(), f"Language mismatch in {filename}"
        assert (df["script"] == expected_script).all(), f"Script mismatch in {filename}"
