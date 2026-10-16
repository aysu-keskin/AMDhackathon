"""Upload the OSHA standard files (deploy/evolus/standards) into the Evolus knowledge library.

Evolus REST API, documented at https://evolus.ai/en/developers ("Knowledge libraries"):
POST /api/v1/memories/{libraryId}/documents?language=en with the file as multipart "file". The language is set
to English because the default is Italian. Indexing runs in the background and uses the workspace's platform
credits, so files already in the library are skipped and a single file can be uploaded first to measure the cost.

Usage: python -m backend.core.evolus_upload --list               # library name, documents and indexing status
       python -m backend.core.evolus_upload 29CFR_1910.147.md    # one file (credit test)
       python -m backend.core.evolus_upload --all                # every file not in the library yet
Settings come from .env: EVOLUS_API_KEY, EVOLUS_APP_ID, EVOLUS_LIBRARY_ID (EVOLUS_BASE_URL optional).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

from dotenv import load_dotenv

from backend.pipeline.paths import ROOT

load_dotenv(ROOT / ".env")

STANDARDS = ROOT / "deploy" / "evolus" / "standards"
BASE_URL = os.environ.get("EVOLUS_BASE_URL", "https://api.evolus.ai/api/v1").rstrip("/")
LIBRARY_NAME = "OSHA 29 CFR 1910 (selected)"


def call(method: str, path: str, body: bytes | None = None, content_type: str | None = None):
    headers = {"X-ApiKey": os.environ["EVOLUS_API_KEY"], "X-Application-Id": os.environ["EVOLUS_APP_ID"]}
    if content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        text = response.read().decode("utf-8")
        return response.status, (json.loads(text) if text.strip() else None)


def items(payload) -> list:
    """The API may answer with a bare list or wrap it ({"items": [...]} and similar)."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "documents", "data", "results", "value"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def field(entry: dict, *names: str):
    return next((entry[n] for n in names if entry.get(n) not in (None, "")), None)


def document_names(library_id: str) -> list[tuple[str, object]]:
    _, payload = call("GET", f"/memories/{library_id}/documents")
    # ingestionStatus 2 with a chunkCount means indexed (seen on the first upload, 16 Oct 2026).
    return [(str(field(d, "title", "fileName", "name") or d),
             f"ingestionStatus={d.get('ingestionStatus')} chunks={d.get('chunkCount')} error={d.get('ingestionError')}")
            for d in items(payload)]


def check_library(library_id: str) -> None:
    # GET /memories (all libraries) is closed to application keys; one library by id is open.
    _, payload = call("GET", f"/memories/{library_id}")
    name = payload.get("name") if isinstance(payload, dict) else None
    print(f"Library {library_id}: {name}")
    if name != LIBRARY_NAME:
        sys.exit(f"Stopping: expected the library '{LIBRARY_NAME}'. Check EVOLUS_LIBRARY_ID in .env.")


def upload(library_id: str, path) -> None:
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
            f"Content-Type: text/markdown\r\n\r\n").encode("utf-8") + path.read_bytes() + \
        f"\r\n--{boundary}--\r\n".encode("utf-8")
    status, _ = call("POST", f"/memories/{library_id}/documents?language=en", body,
                     f"multipart/form-data; boundary={boundary}")
    print(f"  uploaded {path.name} ({path.stat().st_size / 1e3:.0f} kB) -> HTTP {status}")


def main() -> None:
    args = sys.argv[1:]
    missing = [n for n in ("EVOLUS_API_KEY", "EVOLUS_APP_ID", "EVOLUS_LIBRARY_ID") if not os.environ.get(n)]
    if missing or not args:
        sys.exit(f"Missing in .env: {', '.join(missing)}" if missing else __doc__)
    library_id = os.environ["EVOLUS_LIBRARY_ID"]
    try:
        check_library(library_id)
        present = document_names(library_id)
        print(f"Documents in the library: {len(present)}")
        if args == ["--list"]:
            for name, status in present:
                print(f"  {name}: {status}")
            return
        files = sorted(STANDARDS.glob("*.md")) if args == ["--all"] else [STANDARDS / a for a in args]
        not_found = [f.name for f in files if not f.exists()]
        if not_found:
            sys.exit(f"Not found in {STANDARDS}: {', '.join(not_found)}")
        names = {name for name, _ in present}
        todo = [f for f in files if f.name not in names]
        print(f"To upload: {len(todo)} (skipping {len(files) - len(todo)} already in the library)")
        for path in todo:
            upload(library_id, path)
            time.sleep(1.2)  # the workspace allows 60 API requests per minute
    except urllib.error.HTTPError as exc:
        sys.exit(f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:300]}")


if __name__ == "__main__":
    main()
