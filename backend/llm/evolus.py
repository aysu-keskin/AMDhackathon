"""The corrective-action draft through our Evolus agent ("Corrective Action Drafter").

The agent lives in the team's Evolus workspace: its instructions are deploy/evolus/agent_instructions.md, its
knowledge library holds the 36 OSHA sections in deploy/evolus/standards/, and its model is DeepSeek-V4-Flash on
AMD Token Factory. If Evolus isn't configured or fails, analyze.py calls Token Factory directly as before.
Settings come from .env: EVOLUS_BASE_URL, EVOLUS_API_KEY, EVOLUS_APP_ID, EVOLUS_AGENT_ID.
"""
import json
import os
import time
import urllib.error
import urllib.request

from backend.llm.token_factory import Reply, strip_fence


class EvolusAgent:
    def __init__(self):
        self.base_url = os.environ.get("EVOLUS_BASE_URL", "https://api.evolus.ai/api/v1").rstrip("/")
        self.api_key = os.environ.get("EVOLUS_API_KEY")
        self.app_id = os.environ.get("EVOLUS_APP_ID")
        self.agent_id = os.environ.get("EVOLUS_AGENT_ID")
        self.timeout = float(os.environ.get("EVOLUS_TIMEOUT", "150"))
        # The model connected to the agent inside Evolus (shown in the UI next to the call).
        self.model = os.environ.get("EVOLUS_AGENT_MODEL", "DeepSeek-V4-Flash")

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.app_id and self.agent_id)

    def ask(self, prompt: str) -> Reply:
        """One question, no chat history: the agent answers with the same JSON the direct call returns."""
        start = time.perf_counter()
        label = f"{self.model} (Evolus agent)"
        request = urllib.request.Request(
            f"{self.base_url}/agents/{self.agent_id}/ask",
            data=json.dumps({"content": prompt, "skipChatHistory": True}).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "X-Api-Key": self.api_key,
                     "X-Application-Id": self.app_id, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:200]
            return Reply(None, "", label, time.perf_counter() - start, f"HTTP {exc.code}: {detail}")
        except (OSError, ValueError) as exc:  # network errors, timeouts, non-JSON body
            return Reply(None, "", label, time.perf_counter() - start, f"{type(exc).__name__}: {exc}")
        raw = body.get("answer") or ""
        seconds = time.perf_counter() - start
        try:
            data = json.loads(strip_fence(raw))
        except json.JSONDecodeError:
            return Reply(None, raw, label, seconds, "unparseable JSON")
        if isinstance(data, dict):
            data["_citations"] = body.get("citations") or []
        return Reply(data, raw, label, seconds)
