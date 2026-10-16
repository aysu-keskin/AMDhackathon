"""Files to upload into the Evolus workspace by hand.

- deploy/evolus/standards/*.md: one file per OSHA 29 CFR 1910 section (the same 36 sections the API cites)
  for the Evolus knowledge library.
- deploy/evolus/agent_instructions.md: the system instructions for the Evolus agent that drafts actions.

Usage: python -m backend.core.evolus_files
"""
import json
import shutil

from backend.core.analyze import DRAFT_SYSTEM
from backend.pipeline.paths import ROOT
from backend.pipeline.standards import STANDARDS_JSON

OUT = ROOT / "deploy" / "evolus"


def main() -> None:
    data = json.loads(STANDARDS_JSON.read_text(encoding="utf-8"))
    sections: dict[str, list[dict]] = {}
    for entry in data["entries"]:
        sections.setdefault(entry["section"], []).append(entry)

    shutil.rmtree(OUT / "standards", ignore_errors=True)
    (OUT / "standards").mkdir(parents=True)
    for section, parts in sections.items():
        head = parts[0]
        body = "\n\n".join(p["text"] for p in sorted(parts, key=lambda p: p["part"]))
        text = (f"# 29 CFR {section} — {head['topic']}\n\n"
                f"Source: eCFR, {head['heading']}, version {data['ecfr_date']} (U.S. Government work, public domain).\n\n"
                f"{body}\n")
        (OUT / "standards" / f"29CFR_{section}.md").write_text(text, encoding="utf-8")

    (OUT / "agent_instructions.md").write_text(DRAFT_SYSTEM + "\n", encoding="utf-8")
    size = sum(f.stat().st_size for f in (OUT / "standards").iterdir())
    print(f"  {len(sections)} standard files ({size / 1e6:.1f} MB) and agent_instructions.md in {OUT}")


if __name__ == "__main__":
    main()
