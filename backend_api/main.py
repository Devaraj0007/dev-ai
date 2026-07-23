import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path so src.* modules can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env", encoding="utf-8-sig", override=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.ingest import build_index, load_documents, DEFAULT_SOURCE_DIR
from src.agent import ResearchAgent

app = FastAPI(title="Dev AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ingest")
def ingest_documents():
    try:
        stats = build_index()
        docs = load_documents(DEFAULT_SOURCE_DIR)
        doc_names = [fname for fname, _ in docs]
        return {
            "chunks_indexed": stats["num_chunks"],
            "documents": doc_names,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask_question(req: AskRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        agent = ResearchAgent()
        response = agent.ask(req.question.strip())

        sources = []
        if response.citations:
            for c in response.citations:
                sources.append({
                    "marker": c.get("marker", ""),
                    "source": c.get("source", ""),
                    "excerpt": c.get("excerpt", ""),
                })
        elif response.retrieved_chunks:
            for i, c in enumerate(response.retrieved_chunks, start=1):
                sources.append({
                    "marker": f"[{i}]",
                    "source": c.get("source", ""),
                    "excerpt": c.get("text", "")[:200],
                })

        return {
            "answer": response.answer,
            "sources": sources,
            "sources_sufficient": response.sources_sufficient,
            "gap_note": response.gap_note,
            "grounded": response.grounded,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
