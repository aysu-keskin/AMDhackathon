"""Every LLM call in this project goes through AMD Token Factory (AMD-hosted vLLM, OpenAI-compatible).

AMD asked that requests to the Token Factory endpoint be easy to find in the code: this is the one place.
Settings come from .env: TOKEN_FACTORY_BASE_URL, TOKEN_FACTORY_API_KEY, LLM_MODEL, LLM_FALLBACK_MODEL.
"""
import json
import os
import re
import time
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

from backend.pipeline.paths import ROOT

load_dotenv(ROOT / ".env")

FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


@dataclass
class Reply:
    data: dict | None
    raw: str
    model: str
    seconds: float
    error: str | None = None


def strip_fence(text: str) -> str:
    """Gemma on Token Factory wraps JSON in a ```json fence; remove exactly one fence, nothing else."""
    match = FENCE.match(text)
    return match.group(1) if match else text.strip()


class TokenFactory:
    def __init__(self):
        base_url = os.environ.get("TOKEN_FACTORY_BASE_URL")
        api_key = os.environ.get("TOKEN_FACTORY_API_KEY")
        if not base_url or not api_key:
            raise RuntimeError("Set TOKEN_FACTORY_BASE_URL and TOKEN_FACTORY_API_KEY in .env")
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=90)
        self.models = [m for m in (os.environ.get("LLM_MODEL"), os.environ.get("LLM_FALLBACK_MODEL")) if m]
        if not self.models:
            raise RuntimeError("Set LLM_MODEL in .env")

    def json_chat(self, system: str, user: str, retries: int = 3) -> Reply:
        """Ask for a JSON object. Retries with backoff, then falls back to the next model."""
        error = None
        for model in self.models:
            for attempt in range(retries):
                start = time.perf_counter()
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        temperature=0,
                        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    )
                    raw = response.choices[0].message.content or ""
                    seconds = time.perf_counter() - start
                    try:
                        return Reply(json.loads(strip_fence(raw)), raw, model, seconds)
                    except json.JSONDecodeError:
                        return Reply(None, raw, model, seconds, "unparseable JSON")
                except Exception as exc:  # network errors, 429, 503 from the provider
                    error = f"{type(exc).__name__}: {exc}"
                    time.sleep(2 ** attempt * 3)
        return Reply(None, "", self.models[-1], 0.0, error)

    def list_models(self) -> list[str]:
        return [m.id for m in self.client.models.list()]
