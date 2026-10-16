"""Everything the measurement page shows, read from the committed reports.

The code-shift series is precomputed into reports/code_shift.json so the server never re-reads the
full dataset at startup (memory on the free tier).

Usage: python -m backend.core.metrics   # regenerates reports/code_shift.json
"""
import json

from backend.pipeline.paths import ROOT, SIR_PARQUET

REPORTS = ROOT / "reports"
CODE_SHIFT = REPORTS / "code_shift.json"
SHIFT_GROUPS = {"62": "old: struck by object", "42": "old: fall on same level",
                "65": "new: running powered equipment", "41": "new: fall to lower level"}


def read(name: str) -> dict:
    # Empty bands were written as NaN (e.g. source is never "trusted"); NaN isn't valid JSON for browsers.
    return json.loads((REPORTS / name).read_text(encoding="utf-8"), parse_constant=lambda _: None)


def code_system_shift() -> list[dict]:
    """Monthly share of four event groups, Jan 2023 - Dec 2024: the OIICS switch on 2024-01-01."""
    import pandas as pd

    df = pd.read_parquet(SIR_PARQUET, columns=["month", "event_group"])
    df = df[(df["month"] >= "2023-01") & (df["month"] <= "2024-12")]
    share = pd.crosstab(df["month"], df["event_group"], normalize="index")
    return [{"month": month, **{g: round(float(share.loc[month].get(g, 0.0)), 4) for g in SHIFT_GROUPS}}
            for month in share.index]


def load() -> dict:
    return {
        "old_reproduction": read("baseline.json")["old_reproduction"],
        "new_accuracy": read("baseline.json")["new_test"],
        "confidence_test": read("confidence_test.json"),
        "second_opinion": {"strict": read("llm_second_opinion_strict.json"), "rescored": read("llm_second_opinion.json")},
        "code_shift": {"groups": SHIFT_GROUPS, "series": read("code_shift.json")},
    }


if __name__ == "__main__":
    CODE_SHIFT.write_text(json.dumps(code_system_shift(), indent=1), encoding="utf-8")
    print(f"Saved {CODE_SHIFT}")
