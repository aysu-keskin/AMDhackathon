"""Deployment bundle: the exact measured model plus the slices of data the API needs.

Team decision (2026-10-16): commit this small bundle so the hosted API starts in minutes and runs the very
model we measured, instead of re-downloading OSHA data and retraining on the host. The data is derived
from OSHA Severe Injury Reports (U.S. Government work, public domain) and eCFR (public domain).

Usage: python -m backend.core.bundle
"""
import shutil

import joblib
import numpy as np
import pandas as pd

from backend.pipeline.paths import ROOT, SIR_PARQUET
from backend.pipeline.standards import STANDARDS_JSON

BUNDLE = ROOT / "deploy" / "bundle"
BUNDLE_MODEL = BUNDLE / "model.joblib"
BUNDLE_CASES = BUNDLE / "cases_new.parquet"
BUNDLE_STANDARDS = BUNDLE / "standards.json"

CASE_COLUMNS = [
    "upa", "month", "sector3", "narrative_masked", "is_duplicate_copy", "is_short_narrative",
    "event_group", "event_title", "source_group", "source_title", "nature_code3", "nature_title",
    "part_group", "part_title",
]


def main() -> None:
    from backend.core.analyze import LOCAL_MODEL  # the full-size artifact from backend.model.baseline

    BUNDLE.mkdir(parents=True, exist_ok=True)
    models = joblib.load(LOCAL_MODEL)
    for spec in models.values():
        spec["model"][-1].coef_ = spec["model"][-1].coef_.astype(np.float32)  # verified: identical predictions
    joblib.dump(models, BUNDLE_MODEL, compress=9)
    pd.read_parquet(SIR_PARQUET, columns=CASE_COLUMNS, filters=[("code_system", "==", "new")]) \
        .to_parquet(BUNDLE_CASES, index=False, compression="zstd")
    shutil.copy(STANDARDS_JSON, BUNDLE_STANDARDS)
    for f in (BUNDLE_MODEL, BUNDLE_CASES, BUNDLE_STANDARDS):
        print(f"  {f.name:<18} {f.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
