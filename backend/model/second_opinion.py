"""LLM second opinion on event and source, run as pre-registered in reports/PREREG-llm-second-opinion.md.

Usage:
  python -m backend.model.second_opinion --ping     # one call on a 2024 (training-year) report, prints prompt + reply
  python -m backend.model.second_opinion --run      # the single test run on 500 reports from 2025
"""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from backend.llm.token_factory import TokenFactory
from backend.model.baseline import classifiable, fit
from backend.model.confidence import wilson
from backend.pipeline.paths import ROOT, SIR_PARQUET
from backend.retrieval.bm25 import CaseIndex

THRESHOLDS = json.loads((ROOT / "backend" / "model" / "thresholds.json").read_text(encoding="utf-8"))
CACHE = ROOT / "data" / "llm_cache" / "second_opinion.jsonl"
REPORT = ROOT / "reports" / "llm_second_opinion.json"

SAMPLE_SIZE, SEED, TOP_K, NEIGHBOURS = 500, 2026, 5, 5
PASS_ACCURACY, PASS_SHARE = 0.93, 0.55

SYSTEM = (
    "You code workplace injury reports with the OSHA OIICS classification (current version). "
    "Pick the event group (what happened) and the source group (the object, substance or exposure that "
    "directly produced the injury) from the candidates only. Similar reports with OSHA's own codes show how "
    "OSHA applies the rules; follow them. Answer with JSON only: {\"event\": \"<group>\", \"source\": \"<group>\"}."
)


def group_titles(cases: pd.DataFrame, prefix: str) -> dict[str, str]:
    """A readable name per 2-digit group: its two most common full-code titles."""
    titles = cases.groupby(f"{prefix}_group")[f"{prefix}_title"].agg(lambda s: "; ".join(s.value_counts().index[:2]))
    return titles.to_dict()


def top_k(model, texts: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    proba = model.predict_proba(texts)
    order = np.argsort(-proba, axis=1)[:, :TOP_K]
    return model.classes_[order], np.take_along_axis(proba, order, axis=1)


def build_prompt(narrative: str, events: list, sources: list, neighbours: pd.DataFrame, titles: dict) -> str:
    lines = [f"Report:\n{narrative}\n", "Event candidates:"]
    lines += [f"- {g}: {titles['event'].get(g, '')}" for g in events]
    lines += ["", "Source candidates:"]
    lines += [f"- {g}: {titles['source'].get(g, '')}" for g in sources]
    lines += ["", "Similar reports coded by OSHA:"]
    for _, case in neighbours.iterrows():
        lines.append(f"- \"{case['narrative_masked'][:300]}\" -> event {case['event_group']} "
                     f"({case['event_title']}), source {case['source_group']} ({case['source_title']})")
    return "\n".join(lines)


class Experiment:
    def __init__(self):
        df = pd.read_parquet(SIR_PARQUET)
        new = df[df["code_system"] == "new"]
        self.train = new[new["year"] == 2024]
        print("Fitting baseline event/source models on 2024 ...")
        self.models = {name: fit(self.train, f"{name}_group")[:2] for name in ("event", "source")}
        self.index = CaseIndex(self.train)
        self.titles = {p: group_titles(self.train, p) for p in ("event", "source")}
        pool = classifiable(new[(new["year"] == 2025) & new["is_manufacturing"]], "event_group")
        self.sample = pool.sample(n=SAMPLE_SIZE, random_state=SEED)

    def candidates(self, rows: pd.DataFrame) -> dict:
        out = {}
        for name, (model, _) in self.models.items():
            classes, proba = top_k(model, rows["narrative_masked"])
            out[name] = (classes, proba)
        return out

    def prompt_for(self, row: pd.Series, events: list, sources: list) -> str:
        return build_prompt(row["narrative_masked"], events, sources,
                            self.index.search(row["narrative_masked"], NEIGHBOURS), self.titles)


def ping() -> None:
    exp = Experiment()
    row = exp.train.sample(n=1, random_state=1).iloc[0]
    cands = exp.candidates(row.to_frame().T)
    prompt = exp.prompt_for(row, list(cands["event"][0][0]), list(cands["source"][0][0]))
    print(prompt, "\n")
    reply = TokenFactory().json_chat(SYSTEM, prompt)
    print(f"model={reply.model} seconds={reply.seconds:.1f} error={reply.error}\nraw={reply.raw!r}\nparsed={reply.data}")
    print(f"truth: event {row['event_group']}, source {row['source_group']}")


def call_all(exp: Experiment, cands: dict, llm: TokenFactory) -> dict:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    # Later lines override earlier ones. Only real model answers (parsed or not) count as done;
    # infrastructure failures (connection drops, outages) produced no answer and are retried.
    done = {}
    if CACHE.exists():
        for line in CACHE.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            if item["data"] is not None or item["error"] == "unparseable JSON":
                done[item["upa"]] = item

    def work(i: int):
        row = exp.sample.iloc[i]
        if int(row["upa"]) in done:
            return None
        prompt = exp.prompt_for(row, list(cands["event"][0][i]), list(cands["source"][0][i]))
        reply = llm.json_chat(SYSTEM, prompt)
        return {"upa": int(row["upa"]), "data": reply.data, "raw": reply.raw, "model": reply.model,
                "seconds": reply.seconds, "error": reply.error}

    # The rate limiter in TokenFactory keeps us under 20 requests/minute; the key allows 8 concurrent
    # requests for the whole team, so we use 6 and leave 2 for teammates.
    with ThreadPoolExecutor(max_workers=6) as pool, CACHE.open("a", encoding="utf-8") as cache:
        for n, item in enumerate(pool.map(work, range(len(exp.sample))), 1):
            if item:
                cache.write(json.dumps(item) + "\n")
                cache.flush()
                done[item["upa"]] = item
            if n % 50 == 0:
                print(f"  {n}/{len(exp.sample)}")
    return done


def labels_summary(trusted: np.ndarray, human: np.ndarray, correct: np.ndarray) -> dict:
    out = {}
    for name, mask in (("trusted", trusted), ("approximate", ~trusted & ~human), ("human", human)):
        k, n = int(correct[mask].sum()), int(mask.sum())
        out[name] = {"share": round(n / len(correct), 4), "accuracy": round(k / n, 4) if n else None,
                     "accuracy_95ci": wilson(k, n)}
    out["passes"] = bool(out["trusted"]["accuracy"] is not None and out["trusted"]["accuracy"] >= PASS_ACCURACY
                         and out["trusted"]["share"] >= PASS_SHARE)
    return out


def run() -> None:
    exp = Experiment()
    cands = exp.candidates(exp.sample)
    replies = call_all(exp, cands, TokenFactory())
    missing = [u for u in exp.sample["upa"].astype(int)
               if u not in replies or (replies[u]["data"] is None and replies[u]["error"] != "unparseable JSON")]
    if missing:
        print(f"{len(missing)} reports have no model answer (network/provider failures). Run --run again to retry them.")
        return

    s = exp.sample
    event_truth, source_truth = s["event_group"].to_numpy(), s["source_group"].to_numpy()
    event_top, event_proba = cands["event"]
    source_top, _ = cands["source"]
    llm_event, llm_source, seconds, failed, models = [], [], [], 0, {}
    for i, upa in enumerate(s["upa"].astype(int)):
        item = replies[upa]
        data = item["data"] or {}
        e, src = str(data.get("event", "")), str(data.get("source", ""))
        llm_event.append(e if e in event_top[i] else None)
        llm_source.append(src if src in source_top[i] else None)
        failed += item["data"] is None
        seconds.append(item["seconds"])
        models[item["model"]] = models.get(item["model"], 0) + 1

    base_event, conf = event_top[:, 0], event_proba[:, 0]
    rare = np.isin(base_event, list(exp.models["event"][1]))
    human = (conf < THRESHOLDS["event"]["human_below"]) | rare
    agree = np.array([le == be for le, be in zip(llm_event, base_event)])
    correct = base_event == event_truth

    baseline_trusted = (conf >= THRESHOLDS["event"]["trusted_from"]) & ~human
    rule_a = labels_summary(baseline_trusted & agree, human, correct)
    rule_b = labels_summary(~human & agree, human, correct)
    decision = "A" if rule_a["passes"] else None
    if rule_b["passes"] and (decision is None or rule_b["trusted"]["share"] > rule_a["trusted"]["share"]):
        decision = "B"

    reordered_source = np.array([ls if ls else st[0] for ls, st in zip(llm_source, source_top)])
    report = {
        "prereg": "reports/PREREG-llm-second-opinion.md",
        "sample": SAMPLE_SIZE, "seed": SEED, "models_used": models,
        "failed_or_unparseable": failed,
        "latency_seconds": {"median": round(float(np.median(seconds)), 2), "p90": round(float(np.quantile(seconds, 0.9)), 2)},
        "event": {
            "baseline_only": labels_summary(baseline_trusted, human, correct),
            "rule_a": rule_a, "rule_b": rule_b, "decision": decision or "baseline only",
            "baseline_top1_accuracy": round(float(correct.mean()), 4),
            "llm_alone_accuracy": round(float(np.mean([le == t for le, t in zip(llm_event, event_truth)])), 4),
            "truth_in_top5": round(float(np.mean([t in row for t, row in zip(event_truth, event_top)])), 4),
            "agreement": round(float(agree.mean()), 4),
        },
        "source": {
            "baseline_top1_accuracy": round(float((source_top[:, 0] == source_truth).mean()), 4),
            "after_llm_reorder_top1_accuracy": round(float((reordered_source == source_truth).mean()), 4),
            "llm_alone_accuracy": round(float(np.mean([ls == t for ls, t in zip(llm_source, source_truth)])), 4),
            "truth_in_top3": round(float(np.mean([t in row[:3] for t, row in zip(source_truth, source_top)])), 4),
            "truth_in_top5": round(float(np.mean([t in row for t, row in zip(source_truth, source_top)])), 4),
        },
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--ping", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = parser.parse_args()
    ping() if args.ping else run()
