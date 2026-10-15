"""Sample reports for the demo, and their recorded results for replay mode.

The samples are written by the team (synthetic, not OSHA records). Replay results are real outputs of the
pipeline, recorded with a timestamp; the UI labels them as recordings.

Usage: python -m backend.core.samples   # records reports/demo_replay.json (4 live analyses)
"""
import json
from datetime import datetime, timezone

from backend.pipeline.paths import ROOT

REPLAY = ROOT / "reports" / "demo_replay.json"

SAMPLES = [
    {"id": "press", "title": {"en": "Power press, fingertip", "it": "Pressa, polpastrello"},
     "text": "A press operator was trying to remove a stuck part from the die by hand when the mechanical power "
             "press cycled. The tip of his right index finger was amputated. He was taken to the hospital."},
    {"id": "forklift", "title": {"en": "Forklift, pedestrian", "it": "Carrello elevatore, pedone"},
     "text": "An employee was walking through the warehouse aisle when a forklift that was backing up struck him. "
             "He suffered a fractured left leg and was hospitalized."},
    {"id": "conveyor", "title": {"en": "Conveyor jam, hand", "it": "Inceppamento nastro, mano"},
     "text": "While clearing a jam on a running belt conveyor in the packaging line, an employee reached under the "
             "guard and her left hand was pulled into the pinch point at the tail pulley. She suffered crushing "
             "injuries and two fractured fingers."},
    {"id": "fryer", "title": {"en": "Fryer, hot oil burn", "it": "Friggitrice, ustione da olio"},
     "text": "An employee was draining an industrial fryer at a snack food plant when the drain valve opened "
             "suddenly and hot oil splashed onto his forearms. He sustained second-degree burns and was admitted "
             "to the hospital."},
]


def record() -> None:
    from backend.core.analyze import Analyzer

    analyzer = Analyzer()
    recorded = {}
    for sample in SAMPLES:
        result = analyzer.analyze(sample["text"])
        result["recorded_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        recorded[sample["id"]] = result
        print(f"  {sample['id']:<9} {result['seconds_total']:>5.1f} s  "
              f"{len(result['action_plan']['actions'])} actions, {len(result['action_plan']['rejected'])} rejected")
    REPLAY.write_text(json.dumps(recorded, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {REPLAY}")


if __name__ == "__main__":
    record()
