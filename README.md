# DarkSea28 · Workplace Safety Incident Assistant

AMD Developer Hackathon ACT III · Intelligent Industry track.

An assistant for a factory's safety officer: it turns a free-text incident report into OSHA's standard
OIICS codes with a confidence label, finds similar real OSHA cases, and drafts corrective actions that
cite OSHA standards. Uncertain cases are handed to a person.

Background: [project brief](docs/S-Is-Guvenligi-Olay-Asistani.md) · [data exploration](docs/OSHA-SIR-EDA.html)

## Setup

Use **Python 3.12**. On Windows, Python 3.13.13 crashes inside asyncio as soon as SciPy's linear algebra is
loaded (access violation), which takes down the API server.

```bash
py -3.12 -m venv .venv        # Windows; python3.12 -m venv .venv elsewhere
.venv/Scripts/activate        # Windows; use .venv/bin/activate on macOS/Linux
pip install -r backend/requirements.txt
cp .env.example .env          # then fill in the Token Factory key
```

## Run

```bash
uvicorn backend.api.main:app --port 8000      # API (loads models in ~10 s)
npm --prefix frontend install
npm --prefix frontend run dev                 # UI on http://localhost:5173 (proxies /api to :8000)
```

The model file is produced by `python -m backend.model.baseline` (≈ 25 min, CPU) after the data steps below,
and the standards excerpts by `python -m backend.pipeline.standards`.

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

## Deployment (free tiers)

- **API → Railway** (`Dockerfile`, `railway.json`). Set these variables in Railway, never in git:
  `TOKEN_FACTORY_BASE_URL`, `TOKEN_FACTORY_API_KEY`, `LLM_MODEL=Gemma-4-31B-IT`,
  `LLM_FALLBACK_MODEL=DeepSeek-V4-Flash`, `LLM_DRAFT_MODEL=DeepSeek-V4-Flash`. Peak memory ≈ 360 MB.
- **UI → Vercel**: root directory `frontend`, variable `VITE_API_URL=https://<railway-domain>`.
  If the API is unreachable the UI still serves the measurement page and labelled recordings from
  `frontend/public/data` (`python -m backend.core.export_static`).
- **Deployment bundle** (`deploy/bundle`, ≈ 37 MB, `python -m backend.core.bundle`): the exact measured
  model (float32 coefficients: identical top-1 on all 2,628 reports of 2025 manufacturing), the new-system
  case slice used for similar cases, and the eCFR excerpts. Derived from OSHA Severe Injury Reports and
  eCFR, both U.S. Government works in the public domain. Full data is still downloaded by the scripts above.

## License

MIT
