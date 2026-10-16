"""One incident report in, everything the safety officer needs out (single wait for the user).

Flow:
1. Baseline coder (CPU): four codes with probabilities; top candidates for event and source.
2. In parallel on AMD Token Factory:
   a. second opinion on event/source: the exact prompt tested in reports/PREREG-llm-second-opinion.md
   b. corrective-action draft grounded in OSHA standards excerpts
3. Confidence labels: rule B for event (team decision 2026-10-15), thresholds from validation for the rest.
4. Validator drops actions that cite unknown/unprovided standards or use legal/medical verdicts.
"""
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import joblib
import numpy as np
import pandas as pd

from backend.llm.token_factory import TokenFactory
from backend.model.second_opinion import SYSTEM as SECOND_OPINION_SYSTEM
from backend.model.second_opinion import build_prompt, read_group
from backend.pipeline.paths import ROOT, SIR_PARQUET
from backend.pipeline.prepare import DATE_PATTERN
from backend.retrieval.bm25 import CaseIndex
from backend.retrieval.standards import StandardsIndex, validate_actions

MODEL_FILE = ROOT / "data" / "models" / "baseline_new.joblib"
THRESHOLDS = json.loads((ROOT / "backend" / "model" / "thresholds.json").read_text(encoding="utf-8"))
ALWAYS_INCLUDE = ("1910.147", "1910.132")  # lockout/tagout, PPE hazard assessment
# Team decision 2026-10-15: Gemma keeps the tested second opinion; the long action draft goes to a faster
# model (Gemma took 1-4 minutes on it). Gemma is the fallback if the draft model fails.
SECOND_OPINION_MODEL = "Gemma-4-31B-IT"  # the model rule B was measured with
DRAFT_MODELS = [m for m in (os.environ.get("LLM_DRAFT_MODEL", "DeepSeek-V4-Flash"), os.environ.get("LLM_MODEL")) if m]
TITLE_COLUMN = {"event": "event_title", "source": "source_title", "nature": "nature_title", "part": "part_title"}

DRAFT_SYSTEM = (
    "You assist a factory safety officer after a workplace incident. Using only the OSHA standard excerpts "
    "provided, draft corrective actions ordered by the hierarchy of controls (elimination/engineering, "
    "administrative, training, PPE). Each action cites exactly one provided section number (e.g. 1910.212). "
    "Say a standard 'may be relevant'; never state that anyone violated a rule, never give legal conclusions, "
    "never give medical diagnosis or treatment advice. Give 3 to 6 actions and cover more than one level of "
    "the hierarchy when the excerpts allow. Also list up to 4 short questions about facts missing "
    "from the report that would change the actions. Write every text field twice: English (en) and Italian "
    "(it), same meaning. Answer with JSON only: "
    '{"missing_info": [{"en": "...", "it": "..."}], "actions": [{"type": "engineering|administrative|training|ppe", '
    '"standard": "1910.xxx", "action": {"en": "...", "it": "..."}, "why": {"en": "...", "it": "..."}}]}'
)


def label_for(name: str, confidence: float, rare: bool, agree: bool | None, measured_check: bool = True) -> str:
    """measured_check: the second opinion came from the model we measured (Gemma). If not (outage,
    fallback to another model), event falls back to the classifier-only rule, which was also measured."""
    rule = THRESHOLDS[name]
    if confidence < rule["human_below"] or rare:
        return "human"
    if name == "event" and measured_check:
        return "trusted" if agree else "approximate"  # rule B
    if rule["trusted_from"] is not None and confidence >= rule["trusted_from"]:
        return "trusted"
    return "approximate"


class Analyzer:
    def __init__(self):
        self.models = joblib.load(MODEL_FILE)
        cases = pd.read_parquet(SIR_PARQUET)
        cases = cases[cases["code_system"] == "new"]
        self.case_index = CaseIndex(cases)
        self.titles = {
            name: cases.groupby(spec["column"])[TITLE_COLUMN[name]].agg(lambda s: "; ".join(s.value_counts().index[:2])).to_dict()
            for name, spec in self.models.items()
        }
        self.standards = StandardsIndex()
        self.llm = TokenFactory()

    def code(self, text: str) -> dict:
        out = {}
        for name, spec in self.models.items():
            proba = spec["model"].predict_proba([text])[0]
            order = np.argsort(-proba)
            classes = spec["model"].classes_
            out[name] = [{"code": str(classes[i]), "title": self.titles[name].get(classes[i], ""),
                          "confidence": round(float(proba[i]), 4)} for i in order[:5]]
        return out

    def draft_prompt(self, text: str, codes: dict, neighbours: pd.DataFrame, excerpts: list[dict]) -> str:
        lines = [f"Report:\n{text}\n", "Predicted OSHA codes (may be uncertain):"]
        lines += [f"- {name}: {codes[name][0]['title']}" for name in ("event", "source", "nature", "part")]
        lines += ["", "Similar OSHA reports:"]
        lines += [f"- {c['narrative_masked'][:220]}" for _, c in neighbours.head(3).iterrows()]
        lines += ["", "OSHA standard excerpts you may cite:"]
        for e in excerpts:
            lines.append(f"[{e['section']}] {e['topic']}\n{e['text'][:900]}\n")
        return "\n".join(lines)

    def analyze(self, text: str) -> dict:
        started = time.perf_counter()
        # Same preprocessing as training: collapse whitespace, mask dates.
        text = DATE_PATTERN.sub("[DATE]", " ".join(text.split()))
        codes = self.code(text)
        neighbours = self.case_index.search(text, 5)
        event_cands = [c["code"] for c in codes["event"]]
        source_cands = [c["code"] for c in codes["source"]]
        query = f"{text} {codes['event'][0]['title']} {codes['source'][0]['title']}"
        excerpts = self.standards.search(query, k=5)
        # Programs that apply to almost every machine incident; BM25 rarely ranks them first.
        for section in ALWAYS_INCLUDE:
            if section not in {e["section"] for e in excerpts}:
                excerpts.append(self.standards.best_in_section(query, section))

        second_prompt = build_prompt(text, event_cands, source_cands, neighbours,
                                     {"event": self.titles["event"], "source": self.titles["source"]})
        draft_prompt = self.draft_prompt(text, codes, neighbours, excerpts)
        with ThreadPoolExecutor(max_workers=2) as pool:
            second_future = pool.submit(self.llm.json_chat, SECOND_OPINION_SYSTEM, second_prompt)
            draft_future = pool.submit(self.llm.json_chat, DRAFT_SYSTEM, draft_prompt, json_mode=True,
                                       models=DRAFT_MODELS)
            second, draft = second_future.result(), draft_future.result()

        llm_event = read_group((second.data or {}).get("event"), event_cands)
        llm_source = read_group((second.data or {}).get("source"), source_cands)
        # Rule B was measured with Gemma only; another model's agreement is shown but doesn't earn "trusted".
        measured_check = second.data is not None and second.model == SECOND_OPINION_MODEL

        result_codes = {}
        for name, candidates in codes.items():
            top = candidates[0]
            rare = top["code"] in set(self.models[name]["rare"])
            agree = (llm_event == top["code"]) if name == "event" else None
            options = candidates[:3]
            if name == "source" and llm_source and llm_source != top["code"]:
                options = sorted(candidates, key=lambda c: c["code"] != llm_source)[:3]  # LLM pick first
            result_codes[name] = {
                **(options[0] if name == "source" else top),
                "label": label_for(name, top["confidence"], rare, agree, measured_check),
                "alternatives": options[1:] if name == "source" else candidates[1:3],
                "llm_pick": llm_event if name == "event" else llm_source if name == "source" else None,
            }

        actions = (draft.data or {}).get("actions", []) if isinstance(draft.data, dict) else []
        allowed = {e["section"] for e in excerpts}
        kept, rejected = validate_actions(actions, allowed, set(self.standards.sections))

        return {
            "report": text,
            "codes": result_codes,
            "similar_cases": [
                {"upa": int(c["upa"]), "month": c["month"],
                 "sector": None if pd.isna(c["sector3"]) else str(c["sector3"]), "narrative": c["narrative_masked"],
                 "event": f"{c['event_group']} · {c['event_title']}", "source": f"{c['source_group']} · {c['source_title']}",
                 "nature": c["nature_title"], "part": c["part_title"]}
                for _, c in neighbours.iterrows()
            ],
            "action_plan": {
                "missing_info": (draft.data or {}).get("missing_info", []) if isinstance(draft.data, dict) else [],
                "actions": kept,
                "rejected": rejected,
                "standards": [{"section": e["section"], "topic": e["topic"], "excerpt": e["text"][:400]} for e in excerpts],
                "ecfr_date": self.standards.ecfr_date,
            },
            "second_opinion": {
                "model": second.model if second.data is not None else None,
                "measured_model": SECOND_OPINION_MODEL,
                "measured": measured_check,
            },
            "amd": {
                "endpoint": urlparse(str(self.llm.client.base_url)).netloc,
                "calls": [
                    {"purpose": "second opinion (event, source)", "model": second.model,
                     "seconds": round(second.seconds, 1), "error": second.error},
                    {"purpose": "corrective-action draft", "model": draft.model,
                     "seconds": round(draft.seconds, 1), "error": draft.error},
                ],
            },
            "seconds_total": round(time.perf_counter() - started, 1),
        }
