"""BM25 search over OSHA narratives (similar cases).

Narratives are short, English and formulaic, so plain BM25 is a strong start (see the EDA).
Generic duplicate copies and near-empty narratives are left out of the index.
"""
import re

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi

TOKEN = re.compile(r"[a-z0-9]+")
STOPWORDS = frozenset(
    "a an and the of to in on at for with from by was were is be been his her their they he she it its "
    "employee employees worker an that this as into while when after which who".split()
)


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN.findall(text.lower()) if t not in STOPWORDS and t != "date"]


class CaseIndex:
    def __init__(self, cases: pd.DataFrame):
        cases = cases[~cases["is_duplicate_copy"] & ~cases["is_short_narrative"]]
        self.cases = cases.reset_index(drop=True)
        self.bm25 = BM25Okapi([tokenize(t) for t in self.cases["narrative_masked"]])

    def search(self, text: str, k: int = 5) -> pd.DataFrame:
        scores = self.bm25.get_scores(tokenize(text))
        top = np.argsort(-scores)[:k]
        found = self.cases.iloc[top].copy()
        found["score"] = scores[top]
        return found
