from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

SIR_ZIP = RAW_DIR / "January2015toNovember2025.zip"
SIR_CSV = RAW_DIR / "January2015toNovember2025.csv"
SIR_PARQUET = PROCESSED_DIR / "sir.parquet"
