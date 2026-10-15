"""Everything the measurement page shows, read from the committed reports plus one chart series."""
import json

import pandas as pd

from backend.pipeline.paths import ROOT, SIR_PARQUET

REPORTS = ROOT / "reports"
SHIFT_GROUPS = {"62": "old: struck by object", "42": "old: fall on same level",
                "65": "new: running powered equipment", "41": "new: fall to lower level"}


def read(name: str) -> dict:
    return json.loads((REPORTS / name).read_text(encoding="utf-8"))


def code_system_shift() -> list[dict]:
    """Monthly share of four event groups, Jan 2023 - Dec 2024: the OIICS switch on 2024-01-01."""
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
        "code_shift": {"groups": SHIFT_GROUPS, "series": code_system_shift()},
    }
