# DarkSea28 · Workplace Safety Incident Assistant

AMD Developer Hackathon ACT III · Intelligent Industry track.

An assistant for a factory's safety officer: it turns a free-text incident report into OSHA's standard
OIICS codes with a confidence label, finds similar real OSHA cases, and drafts corrective actions that
cite OSHA standards. Uncertain cases are handed to a person.

Background: [project brief](docs/S-Is-Guvenligi-Olay-Asistani.md) · [data exploration](docs/OSHA-SIR-EDA.html)

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows; use .venv/bin/activate on macOS/Linux
pip install -r backend/requirements.txt
cp .env.example .env          # then fill in the keys
```

## Data

OSHA Severe Injury Reports (U.S. Government work, no copyright). The data is not committed; download and
prepare it with:

```bash
python -m backend.pipeline.download
python -m backend.pipeline.prepare
```

This writes `data/processed/sir.parquet`: one row per report, keyed by `upa`, with a `code_system`
column (`old` before 2024-01-01, `new` after; OSHA changed code meanings on that date), normalized code
titles, date-masked narratives, and duplicate/short-narrative flags. Employer, address and coordinates
are left in the raw CSV only.

## License

MIT
