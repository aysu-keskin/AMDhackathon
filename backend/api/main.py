"""HTTP API for the incident assistant.

Run: uvicorn backend.api.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from backend.core.analyze import Analyzer

state = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    state["analyzer"] = Analyzer()  # loads models, case index and standards once
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
