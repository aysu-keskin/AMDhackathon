"""Turn the raw OSHA SIR CSV into data/processed/sir.parquet.

Applies the decisions from docs/OSHA-SIR-EDA.html:
- UPA is the key (ID is not unique).
- OSHA switched OIICS versions on 2024-01-01; the same code means different
  things before and after, so every row carries `code_system` ("old"/"new").
- Nature needs 3 digits (new group 12 mixes fractures and amputations).
- New-system titles have stray spaces and "  " where commas were.
- Narrative dates are masked so models cannot memorise time.
- Generic repeated and very short narratives are flagged, not dropped.
- Employer, address and coordinates stay in the raw CSV only (rejoin via UPA).

Usage: python -m backend.pipeline.prepare
"""
import re

import pandas as pd

from .paths import PROCESSED_DIR, SIR_CSV, SIR_PARQUET

CODE_SYSTEM_SWITCH = pd.Timestamp("2024-01-01")
SHORT_NARRATIVE_CHARS = 40

# Raw column -> processed prefix
CODES = {
    "Event": ("event", "EventTitle"),
    "Source": ("source", "SourceTitle"),
    "Nature": ("nature", "NatureTitle"),
    "Part of Body": ("part", "Part of Body Title"),
    "Secondary Source": ("secondary_source", "Secondary Source Title"),
}

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_PATTERN = re.compile(
    rf"\b(?:{MONTHS})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?"
    r"|\b\d{1,2}/\d{1,2}/\d{2,4}\b"
    r"|\b\d{4}-\d{2}-\d{2}\b",
    flags=re.IGNORECASE,
)


def normalize_title(title: pd.Series) -> pd.Series:
    """' Food and beverage processing machinery  n.e.c.' -> 'Food and beverage processing machinery, n.e.c.'"""
    return (
        title.astype("string")
        .str.strip()
        .str.replace(r"\s{2,}", ", ", regex=True)
        .str.replace(r",\s*,", ",", regex=True)
    )


def prepare(raw: pd.DataFrame) -> pd.DataFrame:
    if not raw["UPA"].is_unique:
        raise ValueError("UPA is no longer unique; the join key assumption is broken.")

    date = pd.to_datetime(raw["EventDate"], format="%m/%d/%Y")
    naics = raw["Primary NAICS"].astype("string").str.strip()
    naics_valid = naics.str.fullmatch(r"\d{6}").fillna(False)
    narrative = raw["Final Narrative"].fillna("").astype("string").str.strip()

    out = pd.DataFrame(
        {
            "upa": raw["UPA"].astype("int64"),
            "osha_id": raw["ID"].astype("int64"),
            "event_date": date,
            "year": date.dt.year.astype("int16"),
            "month": date.dt.to_period("M").astype("string"),
            "code_system": pd.Series(["new" if d >= CODE_SYSTEM_SWITCH else "old" for d in date], dtype="category"),
            "naics": naics.where(naics_valid),
            "sector2": naics.str[:2].where(naics.str[:2].str.fullmatch(r"\d{2}").fillna(False)),
            "sector3": naics.str[:3].where(naics.str[:3].str.fullmatch(r"\d{3}").fillna(False)),
            "state": raw["State"].astype("string"),
            "federal_state": raw["FederalState"].astype("int8"),
            "hospitalized": raw["Hospitalized"].fillna(0).astype("int8"),
            "amputation": raw["Amputation"].fillna(0).astype("int8"),
            "loss_of_eye": raw["Loss of Eye"].fillna(0).astype("int8"),
            # Some rows list several inspections ("1853713;1853717"); keep them all as text.
            "inspection": raw["Inspection"].astype("string").str.replace(r"\.0$", "", regex=True).str.strip(),
            "narrative": narrative,
            "narrative_masked": narrative.str.replace(DATE_PATTERN, "[DATE]", regex=True),
        }
    )
    out["is_manufacturing"] = out["sector2"].isin(["31", "32", "33"])
    out["has_inspection"] = out["inspection"].notna()

    for raw_code, (prefix, raw_title) in CODES.items():
        code = raw[raw_code].astype("Int64").astype("string")
        out[f"{prefix}_code"] = code
        out[f"{prefix}_group"] = code.str[:2]
        out[f"{prefix}_title"] = normalize_title(raw[raw_title])
    out["nature_code3"] = out["nature_code"].str[:3]

    # A handful of rows have a code but no title: borrow the title from the same code in the same system.
    for prefix, _ in CODES.values():
        title = f"{prefix}_title"
        lookup = (
            out.dropna(subset=[title])
            .groupby(["code_system", f"{prefix}_code"], observed=True)[title]
            .agg(lambda s: s.mode().iloc[0])
        )
        missing = out[title].isna() & out[f"{prefix}_code"].notna()
        keys = list(zip(out.loc[missing, "code_system"], out.loc[missing, f"{prefix}_code"]))
        out.loc[missing, title] = [lookup.get(k, pd.NA) for k in keys]

    length = out["narrative"].str.len()
    out["narrative_chars"] = length.astype("int32")
    out["is_short_narrative"] = length < SHORT_NARRATIVE_CHARS
    out["in_duplicate_group"] = out["narrative"].duplicated(keep=False)
    out["is_duplicate_copy"] = out["narrative"].duplicated(keep="first")
    return out


def summarize(df: pd.DataFrame) -> None:
    mfg, new = df["is_manufacturing"], df["code_system"] == "new"
    print(f"rows                  {len(df):>7,}")
    print(f"new code system       {new.sum():>7,}")
    print(f"manufacturing         {mfg.sum():>7,}")
    print(f"manufacturing + new   {(mfg & new).sum():>7,}")
    print(f"short narratives      {df['is_short_narrative'].sum():>7,}")
    print(f"duplicate groups      {df.loc[df['in_duplicate_group'], 'narrative'].nunique():>7,} texts, "
          f"{df['in_duplicate_group'].sum():,} rows, {df['is_duplicate_copy'].sum():,} extra copies")
    print(f"narratives with dates {(df['narrative'] != df['narrative_masked']).mean():>8.1%}")
    print(f"invalid NAICS         {df['naics'].isna().sum():>7,}")
    print(f"with inspection       {df['has_inspection'].mean():>8.1%} "
          f"({df['inspection'].str.contains(';').sum():,} list several)")


def main() -> None:
    raw = pd.read_csv(SIR_CSV, encoding="utf-8", low_memory=False)
    df = prepare(raw)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(SIR_PARQUET, index=False)
    summarize(df)
    print(f"Saved {SIR_PARQUET} ({SIR_PARQUET.stat().st_size / 1e6:.1f} MB, {df.shape[1]} columns)")


if __name__ == "__main__":
    main()
