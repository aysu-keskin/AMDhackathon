"""The corrective-action draft through our Evolus agent ("Corrective Action Drafter").

The agent lives in the team's Evolus workspace: its instructions are deploy/evolus/agent_instructions.md, its
knowledge library holds the 36 OSHA sections in deploy/evolus/standards/, and its model is DeepSeek-V4-Flash on
AMD Token Factory. If Evolus isn't configured or fails, analyze.py calls Token Factory directly as before.

Two ways to reach the agent, chosen with EVOLUS_ENDPOINT:
- "chat" (default): Evolus's documented agent chat (https://evolus.ai/en/developers), OpenAI-compatible:
  POST {EVOLUS_CHAT_URL}/chat/completions, Authorization: Bearer <key>, model "<applicationId>:<agentId>".
  No X-Conversation-Id is sent, so every report starts a new conversation.
- "ask": POST {EVOLUS_BASE_URL}/agents/{agentId}/ask with X-APIKEY + X-Application-Id, the endpoint the Evolus
  web app itself uses; it also returns the library citations.
Settings come from .env: EVOLUS_API_KEY, EVOLUS_APP_ID, EVOLUS_AGENT_ID, and optionally EVOLUS_ENDPOINT,
EVOLUS_CHAT_URL, EVOLUS_BASE_URL, EVOLUS_TIMEOUT, EVOLUS_AGENT_MODEL.
"""
import json
import os
import time
import urllib.error
import urllib.request

from backend.llm.token_factory import Reply, strip_fence


class EvolusAgent:
    def __init__(self):
        self.endpoint = os.environ.get("EVOLUS_ENDPOINT", "chat")
        self.chat_url = os.environ.get("EVOLUS_CHAT_URL", "https://api.evolus.ai/v1").rstrip("/")
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

    @property
    def url(self) -> str:
        if self.endpoint == "ask":
            return f"{self.base_url}/agents/{self.agent_id}/ask"
        return f"{self.chat_url}/chat/completions"

    def ask(self, prompt: str) -> Reply:
        """One question, no chat history: the agent answers with the same JSON the direct call returns.
        Temperature and other model settings come from the agent's page in Evolus, not from the request."""
        start = time.perf_counter()
        label = f"{self.model} (Evolus agent)"
        if self.endpoint == "ask":
            # Header names from the workspace's Developer keys page.
            headers = {"X-APIKEY": self.api_key, "X-Application-Id": self.app_id}
            payload = {"content": prompt, "skipChatHistory": True}
        else:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {"model": f"{self.app_id}:{self.agent_id}", "messages": [{"role": "user", "content": prompt}]}
        request = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"),
                                         headers={**headers, "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:200]
            return Reply(None, "", label, time.perf_counter() - start, f"HTTP {exc.code}: {detail}")
        except (OSError, ValueError) as exc:  # network errors, timeouts, non-JSON body
            return Reply(None, "", label, time.perf_counter() - start, f"{type(exc).__name__}: {exc}")
        seconds = time.perf_counter() - start
        try:
            if self.endpoint == "ask":
                raw, citations = body.get("answer") or "", body.get("citations") or []
            else:
                raw, citations = body["choices"][0]["message"].get("content") or "", []
        except (AttributeError, IndexError, KeyError, TypeError):
            return Reply(None, json.dumps(body)[:200], label, seconds, "unexpected response shape")
        try:
            data = json.loads(strip_fence(raw))
        except json.JSONDecodeError:
            return Reply(None, raw, label, seconds, "unparseable JSON")
        if isinstance(data, dict):
            data["_citations"] = citations
        return Reply(data, raw, label, seconds)
