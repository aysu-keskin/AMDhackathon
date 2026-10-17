"""HTTP API for the incident assistant.

Run: uvicorn backend.api.main:app --reload
"""
import json
import time
from collections import deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.core import metrics
from backend.core.analyze import Analyzer
from backend.core.samples import REPLAY, SAMPLES
from backend.llm.evolus_extractor import EXTENSIONS, EvolusExtractor, ExtractionError

state = {}
extractor = EvolusExtractor()
# Each extraction uses our Evolus workspace and Token Factory budget, and the demo is public until 15 Nov:
# cap size and rate.
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
EXTRACTIONS_PER_HOUR = 30
recent_extractions: deque[float] = deque()


@asynccontextmanager
async def lifespan(_: FastAPI):
    state["analyzer"] = Analyzer()  # loads models, case index and standards once
    state["metrics"] = metrics.load()
    state["replay"] = json.loads(REPLAY.read_text(encoding="utf-8")) if REPLAY.exists() else {}
    yield


app = FastAPI(title="DarkSea28 Incident Assistant", lifespan=lifespan)
# The hosted UI runs on Vercel (*.vercel.app); no cookies are used, so no credentials are allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_origin_regex=r"https://[a-z0-9-]+\.vercel\.app",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class Report(BaseModel):
    text: str = Field(min_length=20, max_length=4000, description="Incident description in English")


@app.get("/api/health")
def health() -> dict:
    # "evolus" tells the UI that drafts go through the Evolus agent (slower, so it shows a longer wait);
    # "extractor" that a PDF report can be read by the Evolus document extractor.
    return {"ok": "analyzer" in state, "evolus": "analyzer" in state and state["analyzer"].evolus.configured,
            "extractor": extractor.configured}


@app.post("/api/extract")
async def extract(request: Request) -> dict:
    """The raw PDF is the body (Content-Type application/pdf)."""
    if not extractor.configured:
        raise HTTPException(503, "The document extractor is not configured")
    content_type = request.headers.get("content-type", "").split(";")[0].strip().lower()
    if content_type not in EXTENSIONS:
        raise HTTPException(415, "Send a PDF file")
    data = await request.body()
    if not data:
        raise HTTPException(400, "The file is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "The file is larger than 5 MB")
    now = time.monotonic()
    while recent_extractions and now - recent_extractions[0] > 3600:
        recent_extractions.popleft()
    if len(recent_extractions) >= EXTRACTIONS_PER_HOUR:
        raise HTTPException(429, "Too many documents this hour; paste the text instead")
    recent_extractions.append(now)
    try:
        return await run_in_threadpool(extractor.extract, data, content_type)
    except ExtractionError as exc:
        raise HTTPException(502, str(exc)) from exc


@app.post("/api/analyze")
async def analyze(report: Report) -> dict:
    if "analyzer" not in state:
        raise HTTPException(503, "Still loading")
    return await run_in_threadpool(state["analyzer"].analyze, report.text)


@app.get("/api/samples")
def samples() -> list[dict]:
    return [{**s, "has_replay": s["id"] in state.get("replay", {})} for s in SAMPLES]


@app.get("/api/replay/{sample_id}")
def replay(sample_id: str) -> dict:
    if sample_id not in state.get("replay", {}):
        raise HTTPException(404, "No recording for this sample")
    return {**state["replay"][sample_id], "replay": True}


@app.get("/api/metrics")
def get_metrics() -> dict:
    return state["metrics"]
