"""Bundle samples, recorded replays and measurement data into the frontend.

The hosted UI uses these when the API is offline (e.g. the free backend tier has expired), so judges
always see the measurement page and labelled recordings.

Usage: python -m backend.core.export_static
"""
import json

from backend.core import metrics
from backend.core.samples import REPLAY, SAMPLES
from backend.pipeline.paths import ROOT

OUT = ROOT / "frontend" / "public" / "data"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    files = {
        "samples.json": [{**s, "has_replay": s["id"] in replay} for s in SAMPLES],
        "replay.json": {k: {**v, "replay": True} for k, v in replay.items()},
        "metrics.json": metrics.load(),
    }
    for name, data in files.items():
        (OUT / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"  {name:<14} {(OUT / name).stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
