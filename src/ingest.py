"""
ingest.py
Loads raw source documents (.txt, .md, .pdf), splits them into retrievable
chunks, and builds a TF-IDF index over those chunks.

Design choice: TF-IDF + cosine similarity implemented in pure Python rather
than a neural embedding model. This keeps the project dependency-light,
portable on Windows, and fully reproducible offline, at the cost of missing
pure semantic (synonym-level) matches. See README "Tradeoffs" for the full
discussion.
"""

from __future__ import annotations

import os
import re
import pickle
import math
from collections import Counter
from dataclasses import dataclass, asdict
from typing import List, Dict

try:
    from pypdf import PdfReader
except ImportError:  # pypdf is optional if the user has no PDF sources
    PdfReader = None

DEFAULT_INDEX_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".index_cache", "index.pkl"
)
DEFAULT_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sources"
)

# Chunks longer than this (characters) get split further, on sentence
# boundaries, so a single retrieved chunk stays small enough to cite precisely.
MAX_CHUNK_CHARS = 700
CHUNK_OVERLAP_SENTENCES = 1

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


@dataclass
class Chunk:
    id: int
    source: str
    text: str


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [token for token in tokens if token not in STOP_WORDS]


def _read_txt_or_md(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _read_pdf(path: str) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf is not installed; run `pip install pypdf` to ingest PDF sources.")
    reader = PdfReader(path)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def load_documents(source_dir: str = DEFAULT_SOURCE_DIR) -> List[tuple]:
    """Returns a list of (filename, raw_text) for every supported file in source_dir."""
    docs = []
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    for fname in sorted(os.listdir(source_dir)):
        path = os.path.join(source_dir, fname)
        if not os.path.isfile(path):
            continue
        lower = fname.lower()
        if lower.endswith((".txt", ".md")):
            text = _read_txt_or_md(path)
        elif lower.endswith(".pdf"):
            text = _read_pdf(path)
        else:
            continue
        if text.strip():
            docs.append((fname, text))

    if not docs:
        raise ValueError(f"No .txt, .md, or .pdf files found in {source_dir}")
    return docs


def _split_sentences(text: str) -> List[str]:
    # Lightweight sentence splitter; good enough for well-formed prose/manuals.
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s for s in sentences if s]


def _paragraphs(text: str) -> List[str]:
    paras = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paras if p.strip()]


def chunk_document(filename: str, text: str, start_id: int) -> List[Chunk]:
    """Splits one document into citation-sized chunks (paragraph-first, then
    sentence-level fallback for long paragraphs), with light sentence overlap
    between adjacent chunks so context isn't lost at a chunk boundary."""
    chunks: List[Chunk] = []
    cid = start_id

    for para in _paragraphs(text):
        if len(para) <= MAX_CHUNK_CHARS:
            chunks.append(Chunk(id=cid, source=filename, text=para))
            cid += 1
            continue

        sentences = _split_sentences(para)
        buf: List[str] = []
        buf_len = 0
        for sent in sentences:
            if buf_len + len(sent) > MAX_CHUNK_CHARS and buf:
                chunks.append(Chunk(id=cid, source=filename, text=" ".join(buf)))
                cid += 1
                buf = buf[-CHUNK_OVERLAP_SENTENCES:] if CHUNK_OVERLAP_SENTENCES else []
                buf_len = sum(len(s) for s in buf)
            buf.append(sent)
            buf_len += len(sent)
        if buf:
            chunks.append(Chunk(id=cid, source=filename, text=" ".join(buf)))
            cid += 1

    return chunks


def build_index(source_dir: str = DEFAULT_SOURCE_DIR, index_path: str = DEFAULT_INDEX_PATH) -> dict:
    """Loads all source docs, chunks them, fits a TF-IDF index over the
    chunks, and persists everything needed for retrieval to disk."""
    docs = load_documents(source_dir)

    all_chunks: List[Chunk] = []
    next_id = 0
    for fname, text in docs:
        doc_chunks = chunk_document(fname, text, next_id)
        all_chunks.extend(doc_chunks)
        next_id += len(doc_chunks)

    tokenized_chunks = [_tokenize(chunk.text) for chunk in all_chunks]
    document_frequencies: Counter[str] = Counter()
    for tokens in tokenized_chunks:
        document_frequencies.update(set(tokens))

    num_documents_total = len(tokenized_chunks)
    idf: Dict[str, float] = {
        token: math.log((1 + num_documents_total) / (1 + df)) + 1.0
        for token, df in document_frequencies.items()
    }

    vectors: List[Dict[str, float]] = []
    norms: List[float] = []
    for tokens in tokenized_chunks:
        counts = Counter(tokens)
        total_terms = sum(counts.values()) or 1
        vector: Dict[str, float] = {}
        for token, count in counts.items():
            token_idf = idf.get(token)
            if token_idf is None:
                continue
            tf = count / total_terms
            weight = tf * token_idf
            if weight > 0:
                vector[token] = weight
        norm = math.sqrt(sum(weight * weight for weight in vector.values()))
        vectors.append(vector)
        norms.append(norm)

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    with open(index_path, "wb") as f:
        pickle.dump(
            {
                "idf": idf,
                "vectors": vectors,
                "norms": norms,
                "chunks": [asdict(c) for c in all_chunks],
            },
            f,
        )

    return {
        "num_documents": len(docs),
        "num_chunks": len(all_chunks),
        "index_path": index_path,
    }


if __name__ == "__main__":
    stats = build_index()
    print(f"Indexed {stats['num_chunks']} chunks from {stats['num_documents']} documents.")
    print(f"Saved index to {stats['index_path']}")
