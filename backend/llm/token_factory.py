"""Every LLM call in this project goes through AMD Token Factory (AMD-hosted vLLM, OpenAI-compatible).

AMD asked that requests to the Token Factory endpoint be easy to find in the code: this is the one place.
Settings come from .env: TOKEN_FACTORY_BASE_URL, TOKEN_FACTORY_API_KEY, LLM_MODEL, LLM_FALLBACK_MODEL.
"""
import json
import os
import re
import threading
import time
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, RateLimitError

from backend.pipeline.paths import ROOT

load_dotenv(ROOT / ".env")

FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)

# Token Factory limits are per key and shared by the whole team: 20 requests/minute, 1 pt/day.
REQUESTS_PER_MINUTE = int(os.environ.get("LLM_REQUESTS_PER_MINUTE", "18"))


class RateLimiter:
    """Spaces request starts evenly so all threads together stay under the per-minute limit."""

    def __init__(self, per_minute: int):
        self.interval = 60.0 / per_minute
        self.lock = threading.Lock()
        self.next_slot = 0.0

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            slot = max(now, self.next_slot)
            self.next_slot = slot + self.interval
        time.sleep(max(0.0, slot - now))


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
        # Gemma on the shared endpoint can take minutes under load; we retry ourselves, so the SDK doesn't.
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=300, max_retries=0)
        self.models = [m for m in (os.environ.get("LLM_MODEL"), os.environ.get("LLM_FALLBACK_MODEL")) if m]
        if not self.models:
            raise RuntimeError("Set LLM_MODEL in .env")
        self.limiter = RateLimiter(REQUESTS_PER_MINUTE)

    def json_chat(self, system: str, user: str, retries: int = 3, network_retries: int = 8) -> Reply:
        """Ask for a JSON object.

        - Our own connection drops or timeouts: wait and retry the SAME model (the model isn't at fault).
        - 429: wait as long as the server asks (Retry-After), same model.
        - 5xx or 400 from the provider: retry a few times, then fall back to the next model.
        """
        error = None
        for model in self.models:
            provider_failures, network_failures = 0, 0
            while provider_failures < retries and network_failures < network_retries:
                self.limiter.wait()
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
                except (APIConnectionError, APITimeoutError) as exc:
                    error = f"{type(exc).__name__}: {exc}"
                    network_failures += 1
                    time.sleep(min(120, 5 * 2 ** network_failures))
                except RateLimitError as exc:
                    error = f"{type(exc).__name__}: {exc}"
                    time.sleep(float(exc.response.headers.get("retry-after", 60)) + 1)
                except APIStatusError as exc:
                    error = f"{type(exc).__name__}: {exc}"
                    provider_failures += 1
                    if exc.status_code == 400:
                        break
                    time.sleep(2 ** provider_failures * 3)
            if network_failures >= network_retries:
                break  # our network is down; another model won't help
        return Reply(None, "", self.models[0], 0.0, error)

    def list_models(self) -> list[str]:
        return [m.id for m in self.client.models.list()]
