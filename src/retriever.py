"""
retriever.py
Loads the TF-IDF index built by ingest.py and retrieves the top-k most
similar chunks for a given query using cosine similarity.
"""

from __future__ import annotations

import math
import os
import pickle
import re
from collections import Counter
from typing import List, Dict

from src.ingest import DEFAULT_INDEX_PATH


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "will",
    "with",
}


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [token for token in tokens if token not in STOP_WORDS]


class Retriever:
    def __init__(self, index_path: str = DEFAULT_INDEX_PATH):
        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"No index found at {index_path}. Run `python -m src.ingest` "
                "(or `python -m src.cli ingest`) first."
            )
        with open(index_path, "rb") as f:
            data = pickle.load(f)

        if "idf" not in data or "vectors" not in data or "norms" not in data:
            from src.ingest import build_index

            build_index(index_path=index_path)
            with open(index_path, "rb") as f:
                data = pickle.load(f)

        self.idf = data["idf"]
        self.vectors = data["vectors"]
        self.norms = data["norms"]
        self.chunks: List[Dict] = data["chunks"]

    def retrieve(self, query: str, top_k: int = 4, min_score: float = 0.05) -> List[Dict]:
        """Returns up to top_k chunks ranked by cosine similarity to the query.
        Chunks scoring below min_score are dropped -- this is what lets the
        agent honestly say 'not found in the sources' instead of forcing a
        weak match into the prompt."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Question must be a non-empty string.")
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")
        if not 0 <= min_score <= 1:
            raise ValueError("min_score must be between 0 and 1.")

        query_tokens = _tokenize(query)
        query_counts = Counter(query_tokens)
        total_terms = sum(query_counts.values()) or 1
        query_vector: Dict[str, float] = {}
        for token, count in query_counts.items():
            token_idf = self.idf.get(token)
            if token_idf is None:
                continue
            weight = (count / total_terms) * token_idf
            if weight > 0:
                query_vector[token] = weight

        query_norm = math.sqrt(sum(weight * weight for weight in query_vector.values()))
        if query_norm == 0:
            return []

        scores = []
        for vector, norm in zip(self.vectors, self.norms):
            if norm == 0:
                scores.append(0.0)
                continue
            dot_product = sum(query_vector.get(token, 0.0) * weight for token, weight in vector.items())
            scores.append(dot_product / (query_norm * norm))

        ranked_idx = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)[:top_k]
        results = []
        for idx in ranked_idx:
            score = float(scores[idx])
            if score < min_score:
                continue
            chunk = dict(self.chunks[idx])
            chunk["score"] = round(score, 4)
            results.append(chunk)
        return results
