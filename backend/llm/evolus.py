"""The corrective-action draft through our Evolus agent ("Corrective Action Drafter").

The agent lives in the team's Evolus workspace: its instructions are deploy/evolus/agent_instructions.md, its
knowledge library holds the 36 OSHA sections in deploy/evolus/standards/, and its model is DeepSeek-V4-Flash on
AMD Token Factory. If Evolus isn't configured or fails, analyze.py calls Token Factory directly as before.

Two ways to reach the agent, chosen with EVOLUS_ENDPOINT:
- "chat" (default): Evolus's documented agent chat (https://evolus.ai/en/developers), OpenAI-compatible:
  POST {EVOLUS_CHAT_URL}/chat/completions, Authorization: Bearer <key>, model "<applicationId>:<agentId>".
  No X-Conversation-Id is sent, so every report starts a new conversation. The answer is streamed: measured on
  16 Oct 2026, the draft took about 3 minutes and the non-streamed request failed with 422 before finishing.
- "ask": POST {EVOLUS_BASE_URL}/agents/{agentId}/ask with X-APIKEY + X-Application-Id, the endpoint the Evolus
  web app itself uses; it also returns the library citations.
Settings come from .env: EVOLUS_API_KEY, EVOLUS_APP_ID, EVOLUS_AGENT_ID, and optionally EVOLUS_ENDPOINT,
EVOLUS_CHAT_URL, EVOLUS_BASE_URL, EVOLUS_TIMEOUT (total seconds), EVOLUS_AGENT_MODEL.
"""
import json
import os
import re
import time
import urllib.error
import urllib.request

from backend.llm.token_factory import Reply

# The agent tends to say what it is doing ("I'll search the knowledge base...") before a ```json block.
FENCED = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def parse_answer(raw: str) -> dict:
    """The JSON object in the agent's answer: the last fenced block that parses, else the outermost braces."""
    for block in reversed(FENCED.findall(raw)):
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            pass
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object in the answer")
    return json.loads(raw[start:end + 1])


class EvolusAgent:
    def __init__(self):
        self.endpoint = os.environ.get("EVOLUS_ENDPOINT", "chat")
        self.chat_url = os.environ.get("EVOLUS_CHAT_URL", "https://api.evolus.ai/v1").rstrip("/")
        self.base_url = os.environ.get("EVOLUS_BASE_URL", "https://api.evolus.ai/api/v1").rstrip("/")
        self.api_key = os.environ.get("EVOLUS_API_KEY")
        self.app_id = os.environ.get("EVOLUS_APP_ID")
        self.agent_id = os.environ.get("EVOLUS_AGENT_ID")
        self.timeout = float(os.environ.get("EVOLUS_TIMEOUT", "240"))
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

    def read_stream(self, response, deadline: float) -> str:
        """Collect the text of an OpenAI-style Server-Sent Events stream, stopping at the total time budget."""
        parts = []
        for line in response:
            if time.perf_counter() > deadline:
                raise TimeoutError(f"no complete answer within {self.timeout:.0f} s")
            line = line.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            event = json.loads(data)
            if event.get("error"):
                raise ValueError(f"stream error: {json.dumps(event['error'])[:200]}")
            delta = ((event.get("choices") or [{}])[0].get("delta") or {}).get("content")
            if delta:
                parts.append(delta)
        return "".join(parts)

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
            payload = {"model": f"{self.app_id}:{self.agent_id}", "stream": True,
                       "messages": [{"role": "user", "content": prompt}]}
        request = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"),
                                         headers={**headers, "Content-Type": "application/json"}, method="POST")
        citations = []
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if self.endpoint == "ask":
                    body = json.loads(response.read().decode("utf-8"))
                    raw, citations = body.get("answer") or "", body.get("citations") or []
                else:
                    raw = self.read_stream(response, start + self.timeout)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:200]
            return Reply(None, "", label, time.perf_counter() - start, f"HTTP {exc.code}: {detail}")
        except (OSError, ValueError, AttributeError) as exc:  # network errors, timeouts, broken stream or body
            return Reply(None, "", label, time.perf_counter() - start, f"{type(exc).__name__}: {exc}")
        seconds = time.perf_counter() - start
        try:
            data = parse_answer(raw)
        except ValueError:  # json.JSONDecodeError is a ValueError
            return Reply(None, raw, label, seconds, "unparseable JSON")
        if isinstance(data, dict):
            data["_citations"] = citations
        return Reply(data, raw, label, seconds)
