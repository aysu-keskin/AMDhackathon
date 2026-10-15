"""Download a curated set of OSHA general-industry standards (29 CFR 1910) from eCFR.

The list covers the source groups behind most manufacturing reports in the EDA: presses and metalworking
machinery, packaging/food machinery, conveyors, forklifts, floors/ladders/falls, hot substances, plus the
cross-cutting programs (lockout/tagout, PPE). Team decision: start with this set, move to all of 1910 only
if it proves too narrow.

Writes data/processed/standards.json: ~1,500-character chunks cited by section, e.g. "1910.212".

Usage: python -m backend.pipeline.standards
"""
import gzip
import json
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from .paths import PROCESSED_DIR

STANDARDS_JSON = PROCESSED_DIR / "standards.json"

SECTIONS = {
    # Machine guarding (Subpart O)
    "1910.212": "General requirements for all machines (guarding, point of operation)",
    "1910.213": "Woodworking machinery",
    "1910.215": "Abrasive wheel machinery",
    "1910.216": "Mills and calenders in the rubber and plastics industries",
    "1910.217": "Mechanical power presses",
    "1910.218": "Forging machines",
    "1910.219": "Mechanical power-transmission apparatus (belts, gears, pulleys)",
    # Hazardous energy
    "1910.147": "Control of hazardous energy (lockout/tagout)",
    # Hand and portable powered tools (Subpart P)
    "1910.242": "Hand and portable powered tools: general",
    "1910.243": "Guarding of portable powered tools",
    "1910.244": "Other portable tools and equipment",
    # Walking-working surfaces (Subpart D)
    "1910.22": "Walking-working surfaces: general requirements",
    "1910.23": "Ladders",
    "1910.25": "Stairways",
    "1910.28": "Duty to have fall protection",
    "1910.29": "Fall protection systems and falling object protection",
    "1910.30": "Training requirements (walking-working surfaces)",
    # Materials handling (Subpart N)
    "1910.176": "Handling materials: general",
    "1910.178": "Powered industrial trucks (forklifts)",
    "1910.179": "Overhead and gantry cranes",
    "1910.184": "Slings",
    # Personal protective equipment (Subpart I)
    "1910.132": "PPE: general requirements and hazard assessment",
    "1910.133": "Eye and face protection",
    "1910.135": "Head protection",
    "1910.136": "Foot protection",
    "1910.138": "Hand protection",
    # Hazardous materials and environments
    "1910.106": "Flammable liquids",
    "1910.146": "Permit-required confined spaces",
    "1910.1200": "Hazard communication",
    # Electrical (Subpart S)
    "1910.303": "Electrical: general requirements",
    "1910.333": "Electrical: selection and use of work practices",
    "1910.335": "Electrical: safeguards for personnel protection",
    # Welding
    "1910.252": "Welding, cutting and brazing: general requirements",
    # Special industries common in manufacturing
    "1910.263": "Bakery equipment",
    "1910.265": "Sawmills",
    # Medical
    "1910.151": "Medical services and first aid",
}

API = "https://www.ecfr.gov/api/versioner/v1"
CHUNK_CHARS = 1500


def latest_date() -> str:
    with urllib.request.urlopen(f"{API}/titles.json", timeout=60) as response:
        titles = json.load(response)["titles"]
    return next(t["latest_issue_date"] for t in titles if t["number"] == 29)


def fetch_section(section: str, date: str) -> ET.Element:
    # eCFR refuses uncompressed responses for full XML.
    url = f"{API}/full/{date}/title-29.xml?part=1910&section={section}"
    request = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": "darksea28-hackathon"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read()
                encoding = response.headers.get("Content-Encoding")
            break
        except (ConnectionError, TimeoutError, urllib.error.URLError):
            if attempt == 4:
                raise
            time.sleep(5 * 2 ** attempt)
    if encoding == "gzip":
        body = gzip.decompress(body)
    return ET.fromstring(body)


def text_of(element: ET.Element) -> str:
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()


def split_chunks(section: str, root: ET.Element) -> list[dict]:
    """Pack consecutive <P> paragraphs into ~CHUNK_CHARS pieces for retrieval.

    eCFR XML is flat and nested lists restart at "(a)", so paragraph letters can't be trusted to mark
    structure. Citations (and the validator) therefore work at section level, e.g. "1910.212".
    """
    heading = text_of(root.find(".//HEAD")) if root.find(".//HEAD") is not None else section
    chunks, buffer = [], []
    for p in root.iter("P"):
        text = text_of(p)
        if not text:
            continue
        if buffer and sum(len(t) for t in buffer) + len(text) > CHUNK_CHARS:
            chunks.append("\n".join(buffer))
            buffer = []
        buffer.append(text)
    if buffer:
        chunks.append("\n".join(buffer))
    return [{"citation": section, "section": section, "heading": heading, "part": i + 1, "text": c}
            for i, c in enumerate(chunks)]


def main() -> None:
    date = latest_date()
    entries = []
    for section, topic in SECTIONS.items():
        chunks = split_chunks(section, fetch_section(section, date))
        for chunk in chunks:
            chunk["topic"] = topic
        entries += chunks
        print(f"  {section:<10} {len(chunks):>3} chunks  {topic}")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    STANDARDS_JSON.write_text(json.dumps({"ecfr_date": date, "entries": entries}, indent=1), encoding="utf-8")
    print(f"Saved {len(entries)} chunks from {len(SECTIONS)} sections (eCFR {date}) to {STANDARDS_JSON}")


if __name__ == "__main__":
    main()
