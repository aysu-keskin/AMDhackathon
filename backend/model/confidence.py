"""Confidence labels for the baseline coder (team decision B, 2026-10-15).

Rules, fixed before the test set is scored:
- "human":       prediction falls into a rare class, or confidence is in the lowest 20% (validation quantile).
- "trusted":     event, nature, part only; confidence >= the lowest threshold whose validation accuracy
                 (among predictions at or above it) is still >= 93%.
- "approximate": everything else. Source is never "trusted"; the UI shows its top 3 for a person to pick.

Thresholds come from models trained on Jan-Oct 2024 and validated on Nov-Dec 2024 manufacturing.
The test (train 2024, test 2025 manufacturing) is run once and reported as is.

Usage: python -m backend.model.confidence
"""
import json
import math

import numpy as np
import pandas as pd

from backend.model.baseline import NEW_TARGETS, classifiable, fit, predict
from backend.pipeline.paths import ROOT, SIR_PARQUET

THRESHOLDS = ROOT / "backend" / "model" / "thresholds.json"
REPORT = ROOT / "reports" / "confidence_test.json"

TARGET_ACCURACY = 0.93
HUMAN_SHARE = 0.20
NEVER_TRUSTED = {"source"}


def trusted_threshold(confidence: np.ndarray, correct: np.ndarray) -> float | None:
    order = np.argsort(-confidence, kind="stable")
    running = np.cumsum(correct[order]) / np.arange(1, len(order) + 1)
    ok = np.nonzero(running >= TARGET_ACCURACY)[0]
    return float(confidence[order][ok.max()]) if len(ok) else None


def derive_thresholds(new: pd.DataFrame) -> dict:
    train = new[new["event_date"] < "2024-11-01"]
    valid = new[(new["event_date"] >= "2024-11-01") & (new["year"] == 2024) & new["is_manufacturing"]]
    thresholds = {}
    for name, column in NEW_TARGETS.items():
        model, rare, _ = fit(train, column)
        scored = classifiable(valid, column)
        pred = predict(model, rare, scored)
        conf = pred["confidence"].to_numpy()
        correct = (pred["pred"] == scored[column]).to_numpy()
        thresholds[name] = {
            "human_below": round(float(np.quantile(conf, HUMAN_SHARE)), 4),
            "trusted_from": None if name in NEVER_TRUSTED else trusted_threshold(conf, correct),
            "valid_rows": int(len(scored)),
        }
        print(f"  {name:<7} human<{thresholds[name]['human_below']:.3f}  trusted>={thresholds[name]['trusted_from']}")
    return thresholds


def label(pred: pd.DataFrame, rule: dict) -> pd.Series:
    out = pd.Series("approximate", index=pred.index)
    if rule["trusted_from"] is not None:
        out[pred["confidence"] >= rule["trusted_from"]] = "trusted"
    out[(pred["confidence"] < rule["human_below"]) | pred["rare"]] = "human"
    return out


def wilson(k: int, n: int) -> list[float]:
    if n == 0:
        return [math.nan, math.nan]
    z, p = 1.96, k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(centre - half, 4), round(centre + half, 4)]


def test_once(new: pd.DataFrame, thresholds: dict) -> dict:
    train = new[new["year"] == 2024]
    test = new[(new["year"] == 2025) & new["is_manufacturing"]]
    report = {}
    for name, column in NEW_TARGETS.items():
        model, rare, _ = fit(train, column)
        scored = classifiable(test, column)
        pred = predict(model, rare, scored)
        correct = pred["pred"] == scored[column]
        labels = label(pred, thresholds[name])
        row = {"rows": int(len(scored)), "accuracy": round(float(correct.mean()), 4), "labels": {}}
        for name_label in ("trusted", "approximate", "human"):
            mask = labels == name_label
            k, n = int(correct[mask].sum()), int(mask.sum())
            row["labels"][name_label] = {"share": round(n / len(scored), 4),
                                         "accuracy": round(k / n, 4) if n else None,
                                         "accuracy_95ci": wilson(k, n)}
        # Error concentration in the "human" band versus the rest (the brief's T4 idea).
        human = labels == "human"
        err_h, err_rest = 1 - correct[human].mean(), 1 - correct[~human].mean()
        row["human_vs_rest_error_ratio"] = round(float(err_h / err_rest), 2) if err_rest else None
        report[name] = row
        parts = "  ".join(f"{k}={v['share']:.0%}@{v['accuracy']}" for k, v in row["labels"].items())
        print(f"  {name:<7} acc={row['accuracy']:.3f}  {parts}  ratio={row['human_vs_rest_error_ratio']}")
    return report


def main() -> None:
    df = pd.read_parquet(SIR_PARQUET)
    new = df[df["code_system"] == "new"]

    print("Thresholds from validation (Nov-Dec 2024, manufacturing)")
    thresholds = derive_thresholds(new)
    THRESHOLDS.write_text(json.dumps(thresholds, indent=2), encoding="utf-8")

    print("Single test run (train 2024, test 2025 manufacturing)")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"rule": "B: target 93%, source never trusted, lowest 20% to human",
                                  "thresholds": thresholds, "test": test_once(new, thresholds)}, indent=2),
                      encoding="utf-8")
    print(f"Saved {THRESHOLDS} and {REPORT}")


if __name__ == "__main__":
    main()
