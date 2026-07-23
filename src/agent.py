"""
agent.py
The core Research Agent. Given a question:
  1. Retrieve relevant chunks from the local TF-IDF index (src/retriever.py).
  2. Ask an LLM (via NVIDIA NIM API, defaults to nvidia/nemotron-3-ultra-550b-a55b) to synthesize
     an answer using ONLY those chunks, citing each claim with a [n] marker
     tied to a numbered source list.
  3. Parse the model's structured JSON response.
  4. Validate that every citation number the model used actually corresponds
     to a chunk we retrieved (a "grounding check") -- this is what prevents
     the agent from silently hallucinating a citation.
"""

from __future__ import annotations

import os
import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
DEFAULT_TOP_K = 4
DEFAULT_MIN_SCORE = 0.05
DEFAULT_TIMEOUT_SECONDS = 30.0

SYSTEM_PROMPT = """You are a research assistant that answers questions strictly \
from a set of numbered source excerpts provided to you. You must never use \
outside knowledge, even if you are confident it is correct.

Rules:
1. Every factual claim in your answer must end with a citation marker like \
[1] or [2], referring to the numbered source excerpt it came from.
2. If a claim draws on multiple sources, cite all of them, e.g. [1][3].
3. If the provided excerpts do not contain enough information to answer the \
question (fully or partially), you must say so explicitly instead of \
guessing or filling gaps with outside knowledge.
4. Do not invent citation numbers. Only use numbers that appear in the \
provided source list.
5. Respond with ONLY a single valid JSON object, no markdown fences, no \
preamble, matching this exact schema:
{
  "answer": "<the answer text, with inline [n] citation markers>",
  "sources_sufficient": <true or false>,
  "gap_note": "<if sources_sufficient is false, a one-sentence note on what \
is missing; otherwise an empty string>"
}
"""

GENERAL_SYSTEM_PROMPT = """You are a helpful, capable general-purpose AI assistant.
Answer the user's question directly, clearly, and naturally using your general
knowledge and reasoning. Do not mention source excerpts, document availability,
citations, retrieval, or system limitations unless the user asks about them.

You may receive relevant private document excerpts. Use them when helpful and
prefer their facts for questions about those documents, but do not reveal that
you used them. If the question is ambiguous, make a sensible best effort and
briefly state any important uncertainty instead of refusing.

Respond with ONLY a single valid JSON object, no markdown fences or preamble:
{
  "answer": "<a complete, helpful answer>",
  "sources_sufficient": true,
  "gap_note": ""
}
"""


@dataclass
class AgentResponse:
    question: str
    answer: str
    sources_sufficient: bool
    gap_note: str
    citations: List[Dict] = field(default_factory=list)
    retrieved_chunks: List[Dict] = field(default_factory=list)
    grounded: bool = True
    ungrounded_markers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "question": self.question,
            "answer": self.answer,
            "sources_sufficient": self.sources_sufficient,
            "gap_note": self.gap_note,
            "citations": self.citations,
            "grounded": self.grounded,
            "ungrounded_markers": self.ungrounded_markers,
            "retrieved_chunks": self.retrieved_chunks,
        }


class ResearchAgent:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        mode: Optional[str] = None,
    ):
        api_key = api_key or os.environ.get("NVIDIA_API_KEY")
        if not api_key:
            raise RuntimeError(
                "No NVIDIA API key found. Set NVIDIA_API_KEY in your "
                "environment or .env file."
            )
        self.model = model or os.environ.get("RESEARCH_AGENT_MODEL") or os.environ.get("RESEARCH_MODEL", DEFAULT_MODEL)
        self.top_k = top_k if top_k is not None else _positive_int_env("RESEARCH_AGENT_TOP_K", DEFAULT_TOP_K)
        self.min_score = (
            min_score if min_score is not None else _score_env("RESEARCH_AGENT_MIN_SCORE", DEFAULT_MIN_SCORE)
        )
        self.mode = (mode or os.environ.get("RESEARCH_AGENT_MODE", "research")).strip().lower()
        if not self.model.strip():
            raise ValueError("RESEARCH_AGENT_MODEL must not be empty.")
        if self.top_k < 1:
            raise ValueError("RESEARCH_AGENT_TOP_K must be at least 1.")
        if not 0 <= self.min_score <= 1:
            raise ValueError("RESEARCH_AGENT_MIN_SCORE must be between 0 and 1.")
        if self.mode not in {"general", "research"}:
            raise ValueError("RESEARCH_AGENT_MODE must be either 'general' or 'research'.")

        self.client = OpenAI(
            api_key=api_key,
            base_url=NVIDIA_BASE_URL,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            max_retries=2,
        )
        self.retriever = None
        if self.mode == "research":
            from src.retriever import Retriever

            self.retriever = Retriever()

    def _build_user_prompt(self, question: str, chunks: List[Dict]) -> str:
        if not chunks:
            source_block = "(No source excerpts were retrieved for this question.)"
        else:
            lines = []
            for i, c in enumerate(chunks, start=1):
                lines.append(f"[{i}] (source file: {c['source']})\n{c['text']}")
            source_block = "\n\n".join(lines)

        return (
            f"Source excerpts:\n\n{source_block}\n\n"
            f"Question: {question}\n\n"
            "Answer the question following the system rules exactly."
        )

    def _parse_model_json(self, raw_text: str) -> Dict:
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```(?:json)?|```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback: extract the first {...} block if the model added stray text.
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise

    def _validate_grounding(self, answer: str, chunks: List[Dict], sources_sufficient: bool) -> tuple:
        """Checks every [n] marker in the answer against the retrieved chunk
        list. Returns (is_grounded, list_of_invalid_markers, citations)."""
        used_numbers = sorted(set(int(n) for n in re.findall(r"\[(\d+)\]", answer)))
        valid_range = set(range(1, len(chunks) + 1))

        invalid = [n for n in used_numbers if n not in valid_range]
        missing_citation = sources_sufficient and not used_numbers
        citations = [
            {
                "marker": f"[{n}]",
                "chunk_id": chunks[n - 1]["id"],
                "source": chunks[n - 1]["source"],
                "excerpt": chunks[n - 1]["text"][:200],
            }
            for n in used_numbers
            if n in valid_range
        ]
        invalid_markers = [f"[{n}]" for n in invalid]
        if missing_citation:
            invalid_markers.append("[missing citation]")
        return not invalid_markers, invalid_markers, citations

    def ask(self, question: str) -> AgentResponse:
        if self.mode == "research":
            chunks = self.retriever.retrieve(question, top_k=self.top_k, min_score=self.min_score)
        else:
            chunks = []

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": GENERAL_SYSTEM_PROMPT if self.mode == "general" else SYSTEM_PROMPT},
                    {"role": "user", "content": self._build_user_prompt(question, chunks)},
                ],
            )
        except APIStatusError as e:
            # Surface NVIDIA's own error body (e.g. invalid key, model not
            # found) rather than a bare stack trace.
            detail = getattr(e, "message", str(e))
            raise RuntimeError(f"NVIDIA API error ({e.status_code}): {detail}") from e
        except APITimeoutError as e:
            raise RuntimeError("NVIDIA request timed out after retries. Please try again.") from e
        except APIConnectionError as e:
            raise RuntimeError(f"Could not reach NVIDIA API: {e}") from e

        raw_text = completion.choices[0].message.content or ""

        try:
            parsed = self._parse_model_json(raw_text)
            if not isinstance(parsed, dict):
                raise ValueError("Response JSON must be an object.")
            answer = parsed.get("answer", "")
            sources_sufficient = parsed.get("sources_sufficient", False)
            gap_note = parsed.get("gap_note", "")
            if not isinstance(answer, str) or not isinstance(sources_sufficient, bool) or not isinstance(gap_note, str):
                raise ValueError("Response JSON did not match the required schema.")
            answer = answer.strip()
            gap_note = gap_note.strip()
            if not answer:
                raise ValueError("Response JSON contained an empty answer.")
            if not sources_sufficient and not gap_note:
                gap_note = "The retrieved sources do not contain enough information to answer this question."
        except (json.JSONDecodeError, AttributeError, ValueError):
            # Degrade gracefully: surface the raw text rather than crashing,
            # and flag it clearly as a parse failure so it's never mistaken
            # for a validated, grounded answer.
            answer = raw_text.strip()
            sources_sufficient = False
            gap_note = "Model response could not be parsed as structured JSON."

        if self.mode == "research":
            grounded, invalid_markers, citations = self._validate_grounding(
                answer, chunks, sources_sufficient
            )
        else:
            grounded, invalid_markers, citations = True, [], []

        return AgentResponse(
            question=question,
            answer=answer,
            sources_sufficient=sources_sufficient,
            gap_note=gap_note,
            citations=citations,
            retrieved_chunks=[{"chunk_id": c["id"], "source": c["source"], "score": c["score"]} for c in chunks],
            grounded=grounded,
            ungrounded_markers=invalid_markers,
        )


def _positive_int_env(name: str, default: int) -> int:
    value = os.environ.get(name, str(default))
    try:
        parsed = int(value)
    except ValueError as e:
        raise ValueError(f"{name} must be an integer.") from e
    return parsed


def _score_env(name: str, default: float) -> float:
    value = os.environ.get(name, str(default))
    try:
        return float(value)
    except ValueError as e:
        raise ValueError(f"{name} must be a number between 0 and 1.") from e
