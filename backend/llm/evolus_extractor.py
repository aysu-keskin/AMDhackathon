"""Read an incident report from a PDF form with our Evolus document extractor.

The extractor lives in the team's Evolus workspace (DarkSea28). It reads the PDF's text layer and returns the
fields we defined there as JSON: an English narrative of what happened plus a few facts. Its model is our own
Token Factory connection. Reading a text PDF used no platform credits in our test; scans and photos would need
Evolus OCR (about 10 credits per page, and a worse narrative in our test), so only PDFs are accepted. The API
still limits file size and the number of extractions per hour (main.py).

Evolus REST API, documented at https://evolus.ai/en/developers ("Document extractors"):
POST {EVOLUS_BASE_URL}/agents/{agentId}/json/{extractorId}/ask-file?useWebhook=false, multipart "file".
Settings come from .env: EVOLUS_API_KEY, EVOLUS_APP_ID, EVOLUS_EXTRACTOR_AGENT_ID, EVOLUS_EXTRACTOR_ID.
"""
import json
import os
import time
import urllib.error
import urllib.request
import uuid

EXTENSIONS = {"application/pdf": "pdf"}


class ExtractionError(Exception):
    """Evolus could not read the file; the message is safe to show to the user."""


class EvolusExtractor:
    def __init__(self):
        self.base_url = os.environ.get("EVOLUS_BASE_URL", "https://api.evolus.ai/api/v1").rstrip("/")
        self.api_key = os.environ.get("EVOLUS_API_KEY")
        self.app_id = os.environ.get("EVOLUS_APP_ID")
        self.agent_id = os.environ.get("EVOLUS_EXTRACTOR_AGENT_ID")
        self.extractor_id = os.environ.get("EVOLUS_EXTRACTOR_ID")
        self.timeout = float(os.environ.get("EVOLUS_EXTRACTOR_TIMEOUT", "120"))

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.app_id and self.agent_id and self.extractor_id)

    def extract(self, data: bytes, content_type: str) -> dict:
        start = time.perf_counter()
        boundary = uuid.uuid4().hex
        body = (f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="file"; filename="report.{EXTENSIONS[content_type]}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n").encode("utf-8") + data + f"\r\n--{boundary}--\r\n".encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/agents/{self.agent_id}/json/{self.extractor_id}/ask-file?useWebhook=false",
            data=body,
            headers={"X-APIKEY": self.api_key, "X-Application-Id": self.app_id,
                     "Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                text = response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:200]
            if exc.code == 402:
                raise ExtractionError("The Evolus workspace has no platform credits left for reading documents.") from exc
            raise ExtractionError(f"Evolus could not read the document (HTTP {exc.code}). {detail}") from exc
        except (OSError, ValueError) as exc:
            raise ExtractionError(f"Evolus did not answer in time ({type(exc).__name__}).") from exc
        try:
            fields = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ExtractionError("Evolus returned something that is not JSON.") from exc
        # The body is the extracted data; accept it also when wrapped in a field or sent as a JSON string.
        if isinstance(fields, dict) and "narrative" not in fields:
            for key in ("data", "result", "output", "content"):
                inner = fields.get(key)
                if isinstance(inner, str):
                    try:
                        inner = json.loads(inner)
                    except json.JSONDecodeError:
                        continue
                if isinstance(inner, dict):
                    fields = inner
                    break
        if not isinstance(fields, dict) or not str(fields.get("narrative") or "").strip():
            raise ExtractionError("No incident description was found in the document (a scanned PDF has no text to read).")
        return {"fields": fields, "seconds": round(time.perf_counter() - start, 1)}
