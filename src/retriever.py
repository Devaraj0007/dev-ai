"""
retriever.py
Loads the TF-IDF index built by ingest.py and retrieves the top-k most
similar chunks for a given query using cosine similarity.
"""

from __future__ import annotations

import os
import pickle
from typing import List, Dict

from sklearn.metrics.pairwise import cosine_similarity

from src.ingest import DEFAULT_INDEX_PATH


class Retriever:
    def __init__(self, index_path: str = DEFAULT_INDEX_PATH):
        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"No index found at {index_path}. Run `python -m src.ingest` "
                "(or `python -m src.cli ingest`) first."
            )
        with open(index_path, "rb") as f:
            data = pickle.load(f)

        self.vectorizer = data["vectorizer"]
        self.matrix = data["matrix"]
        self.chunks: List[Dict] = data["chunks"]

    def retrieve(self, query: str, top_k: int = 4, min_score: float = 0.05) -> List[Dict]:
        """Returns up to top_k chunks ranked by cosine similarity to the query.
        Chunks scoring below min_score are dropped -- this is what lets the
        agent honestly say 'not found in the sources' instead of forcing a
        weak match into the prompt."""
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()

        ranked_idx = scores.argsort()[::-1][:top_k]
        results = []
        for idx in ranked_idx:
            score = float(scores[idx])
            if score < min_score:
                continue
            chunk = dict(self.chunks[idx])
            chunk["score"] = round(score, 4)
            results.append(chunk)
        return results
