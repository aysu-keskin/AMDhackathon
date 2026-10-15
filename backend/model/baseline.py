"""Baseline coder: TF-IDF (words + bigrams) + logistic regression, one model per code.

Decisions fixed before looking at any result (see docs/ and the team Q&A):
- Product model: new OIICS system (2024+), all sectors. Evaluation: train 2024, test 2025 manufacturing.
- Old-system model only reproduces the brief's 2023 test (train 2015-2021, test 2023 manufacturing).
- Targets: 2-digit groups; nature uses 3 digits in the new system (group 12 mixes fractures and amputations).
- Group 99 (nonclassifiable / unspecified) is excluded per target.
- Classes with fewer than 30 training examples are "rare": predictions into them go to a person.
- Confidence thresholds are NOT chosen here. We only print the validation coverage/accuracy table
  (train Jan-Oct 2024, validate Nov-Dec 2024) and test accuracy; T3/T4 on test wait for the threshold decision.

Usage: python -m backend.model.baseline
"""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from backend.pipeline.paths import ROOT, SIR_PARQUET

MODELS_DIR = ROOT / "data" / "models"
REPORT = ROOT / "reports" / "baseline.json"

RARE_MIN_EXAMPLES = 30
COVERAGES = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)

NEW_TARGETS = {"event": "event_group", "source": "source_group", "nature": "nature_code3", "part": "part_group"}
OLD_TARGETS = {"event": "event_group", "source": "source_group", "nature": "nature_group", "part": "part_group"}


def make_model():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, max_features=100_000),
        LogisticRegression(max_iter=3000, C=10.0),
    )


def classifiable(df: pd.DataFrame, column: str) -> pd.DataFrame:
    return df[df[column].notna() & (df[column] != "99")]


def train_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Training drops generic duplicate copies and near-empty narratives; test keeps every row."""
    return df[~df["is_duplicate_copy"] & ~df["is_short_narrative"]]


def fit(train: pd.DataFrame, column: str):
    train = classifiable(train_rows(train), column)
    model = make_model().fit(train["narrative_masked"], train[column])
    counts = train[column].value_counts()
    rare = set(counts[counts < RARE_MIN_EXAMPLES].index)
    return model, rare, len(train)


def predict(model, rare: set, test: pd.DataFrame) -> pd.DataFrame:
    proba = model.predict_proba(test["narrative_masked"])
    classes = model.classes_
    top = proba.argmax(axis=1)
    out = pd.DataFrame({"pred": classes[top], "confidence": proba[np.arange(len(top)), top]}, index=test.index)
    out["rare"] = out["pred"].isin(rare)
    return out


def coverage_table(truth: pd.Series, pred: pd.DataFrame) -> list[dict]:
    """Accuracy among the most confident X% (rare-class predictions always count as not confident)."""
    correct = (pred["pred"] == truth).to_numpy()
    order = np.argsort(-np.where(pred["rare"], -1.0, pred["confidence"].to_numpy()), kind="stable")
    rows = []
    for coverage in COVERAGES:
        k = max(1, int(round(coverage * len(order))))
        chosen = order[:k]
        rows.append({
            "coverage": coverage,
            "n": int(k),
            "accuracy": round(float(correct[chosen].mean()), 4),
            "min_confidence": round(float(pred["confidence"].to_numpy()[chosen].min()), 4),
        })
    return rows


def t3_t4(truth: pd.Series, pred: pd.DataFrame) -> dict:
    """The brief's definitions: T3 = accuracy in the most confident 70%; T4 = error rate in the least
    confident 20% divided by the error rate in the other 80%."""
    correct = (pred["pred"] == truth).to_numpy()
    order = np.argsort(-pred["confidence"].to_numpy(), kind="stable")
    n = len(order)
    top70 = order[: int(round(0.7 * n))]
    bottom20 = order[n - int(round(0.2 * n)):]
    rest80 = order[: n - int(round(0.2 * n))]
    err_low, err_rest = 1 - correct[bottom20].mean(), 1 - correct[rest80].mean()
    return {"t3_top70_accuracy": round(float(correct[top70].mean()), 4),
            "t4_error_ratio": round(float(err_low / err_rest), 2) if err_rest else None}


def evaluate(train: pd.DataFrame, test: pd.DataFrame, targets: dict, with_confidence: bool) -> dict:
    results = {}
    for name, column in targets.items():
        model, rare, n_train = fit(train, column)
        scored = classifiable(test, column)
        pred = predict(model, rare, scored)
        truth = scored[column]
        row = {
            "train_rows": n_train,
            "test_rows": len(scored),
            "classifiable_share": round(len(scored) / len(test), 4),
            "classes": len(model.classes_),
            "rare_classes": len(rare),
            "accuracy": round(float((pred["pred"] == truth).mean()), 4),
            "rare_prediction_share": round(float(pred["rare"].mean()), 4),
        }
        if with_confidence:
            row.update(t3_t4(truth, pred))
        results[name] = row
        print(f"  {name:<7} acc={row['accuracy']:.3f}  test={row['test_rows']:,}  classes={row['classes']}  rare={row['rare_classes']}")
    return results


def validation_tables(new: pd.DataFrame) -> dict:
    train = new[new["event_date"] < "2024-11-01"]
    valid = new[(new["event_date"] >= "2024-11-01") & (new["year"] == 2024) & new["is_manufacturing"]]
    tables = {}
    for name, column in NEW_TARGETS.items():
        model, rare, _ = fit(train, column)
        scored = classifiable(valid, column)
        tables[name] = coverage_table(scored[column], predict(model, rare, scored))
    return {"train": "2024-01..2024-10, all sectors", "valid": "2024-11..2024-12, manufacturing",
            "valid_rows": int(len(valid)), "tables": tables}


def main() -> None:
    df = pd.read_parquet(SIR_PARQUET)
    old, new = df[df["code_system"] == "old"], df[df["code_system"] == "new"]
    report = {}

    print("Old system: train 2015-2021, test 2023 manufacturing (reproducing the brief)")
    report["old_reproduction"] = evaluate(
        old[old["year"] <= 2021], old[(old["year"] == 2023) & old["is_manufacturing"]], OLD_TARGETS, True)

    print("New system: train 2024, test 2025 manufacturing (accuracy only until thresholds are chosen)")
    report["new_test"] = evaluate(
        new[new["year"] == 2024], new[(new["year"] == 2025) & new["is_manufacturing"]], NEW_TARGETS, False)

    print("New system: validation coverage tables (Nov-Dec 2024)")
    report["new_validation"] = validation_tables(new)

    print("Product model: retrain on 2024+2025, all sectors")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    product = {}
    for name, column in NEW_TARGETS.items():
        model, rare, n = fit(new, column)
        product[name] = {"model": model, "rare": sorted(rare), "column": column, "train_rows": n}
    joblib.dump(product, MODELS_DIR / "baseline_new.joblib", compress=3)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Saved {REPORT} and {MODELS_DIR / 'baseline_new.joblib'}")


if __name__ == "__main__":
    main()
