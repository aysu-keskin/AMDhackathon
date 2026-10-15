"""HTTP API for the incident assistant.

Run: uvicorn backend.api.main:app --reload
"""
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.core import metrics
from backend.core.analyze import Analyzer
from backend.core.samples import REPLAY, SAMPLES

state = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    state["analyzer"] = Analyzer()  # loads models, case index and standards once
    state["metrics"] = metrics.load()
    state["replay"] = json.loads(REPLAY.read_text(encoding="utf-8")) if REPLAY.exists() else {}
    yield


app = FastAPI(title="DarkSea28 Incident Assistant", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])


class Report(BaseModel):
    text: str = Field(min_length=20, max_length=4000, description="Incident description in English")


@app.get("/api/health")
def health() -> dict:
    return {"ok": "analyzer" in state}


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
