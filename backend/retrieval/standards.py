"""Search the curated OSHA standards and check what the LLM cites.

The validator is the part the LLM can't talk its way around: every cited section must be in our
index AND among the excerpts we gave it, and legal or medical verdicts are rejected.
"""
import json
import re

import numpy as np
from rank_bm25 import BM25Okapi

from backend.pipeline.standards import STANDARDS_JSON
from backend.retrieval.bm25 import tokenize as case_tokenize


def tokenize(text: str) -> list[str]:
    """Case tokenizer plus crude singular forms ("forklifts" -> "forklift").

    Kept separate from the similar-case tokenizer, which feeds the tested second-opinion prompt.
    """
    return [t[:-1] if len(t) > 4 and t.endswith("s") and not t.endswith("ss") else t for t in case_tokenize(text)]

CITATION = re.compile(r"\b1910\.\d+\b")
FORBIDDEN = re.compile(
    r"\b(violat\w*|non-?complian\w*|in breach|is liable|liability|penalt\w*|citation was issued|"
    r"diagnos\w*|prescrib\w*|medication|treatment plan)\b",
    re.IGNORECASE,
)


class StandardsIndex:
    def __init__(self):
        data = json.loads(STANDARDS_JSON.read_text(encoding="utf-8"))
        self.ecfr_date = data["ecfr_date"]
        self.entries = data["entries"]
        self.sections = {e["section"]: e["topic"] for e in self.entries}
        self.bm25 = BM25Okapi([tokenize(f"{e['topic']} {e['heading']} {e['text']}") for e in self.entries])
        # Long chunks drown the section's subject; score the short topic/heading separately too.
        self.section_ids = sorted(self.sections)
        headings = {e["section"]: e["heading"] for e in self.entries}
        self.topic_bm25 = BM25Okapi([tokenize(f"{self.sections[s]} {headings[s]}") for s in self.section_ids])

    def scores(self, query: str) -> np.ndarray:
        tokens = tokenize(query)
        chunk = self.bm25.get_scores(tokens)
        topic = dict(zip(self.section_ids, self.topic_bm25.get_scores(tokens)))
        chunk = chunk / (chunk.max() or 1.0)
        top_topic = max(topic.values()) or 1.0
        return chunk + np.array([topic[e["section"]] / top_topic for e in self.entries])

    def search(self, query: str, k: int = 6, per_section: int = 1) -> list[dict]:
        """Top excerpts, at most `per_section` per section so the LLM sees several standards."""
        scores = self.scores(query)
        picked, seen = [], {}
        for i in np.argsort(-scores):
            entry = self.entries[i]
            if seen.get(entry["section"], 0) >= per_section:
                continue
            seen[entry["section"]] = seen.get(entry["section"], 0) + 1
            picked.append({**entry, "score": float(scores[i])})
            if len(picked) == k:
                break
        return picked


    def best_in_section(self, query: str, section: str) -> dict:
        scores = self.scores(query)
        best = max((i for i, e in enumerate(self.entries) if e["section"] == section), key=lambda i: scores[i])
        return {**self.entries[best], "score": float(scores[best])}


def validate_actions(actions: list[dict], allowed_sections: set[str], known_sections: set[str]) -> tuple[list, list]:
    """Keep actions whose citations are known and were in the excerpts; drop verdict language."""
    kept, rejected = [], []
    for action in actions:
        text = " ".join(str(action.get(k, "")) for k in ("action", "why", "standard"))
        cited = set(CITATION.findall(text))
        problems = []
        if not cited:
            problems.append("no OSHA standard cited")
        if cited - known_sections:
            problems.append(f"unknown standard {sorted(cited - known_sections)}")
        elif cited - allowed_sections:
            problems.append(f"standard not in the provided excerpts {sorted(cited - allowed_sections)}")
        if FORBIDDEN.search(text):
            problems.append("legal or medical verdict language")
        (rejected if problems else kept).append({**action, "problems": problems} if problems else action)
    return kept, rejected
