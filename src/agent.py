"""
agent.py
The core Research Agent. Given a question:
  1. Retrieve relevant chunks from the local TF-IDF index (src/retriever.py).
  2. Ask Claude to synthesize an answer using ONLY those chunks, citing each
     claim with a [n] marker tied to a numbered source list.
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

from anthropic import Anthropic

from src.retriever import Retriever

DEFAULT_MODEL = os.environ.get("RESEARCH_AGENT_MODEL", "claude-sonnet-4-6")
DEFAULT_TOP_K = int(os.environ.get("RESEARCH_AGENT_TOP_K", "4"))

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
        model: str = DEFAULT_MODEL,
        top_k: int = DEFAULT_TOP_K,
    ):
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "No Anthropic API key found. Set ANTHROPIC_API_KEY in your "
                "environment or .env file."
            )
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.top_k = top_k
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

    def _validate_grounding(self, answer: str, chunks: List[Dict]) -> tuple:
        """Checks every [n] marker in the answer against the retrieved chunk
        list. Returns (is_grounded, list_of_invalid_markers, citations)."""
        used_numbers = sorted(set(int(n) for n in re.findall(r"\[(\d+)\]", answer)))
        valid_range = set(range(1, len(chunks) + 1))

        invalid = [n for n in used_numbers if n not in valid_range]
        citations = [
            {
                "marker": f"[{n}]",
                "source": chunks[n - 1]["source"],
                "excerpt": chunks[n - 1]["text"][:200],
            }
            for n in used_numbers
            if n in valid_range
        ]
        is_grounded = len(invalid) == 0
        return is_grounded, [f"[{n}]" for n in invalid], citations

    def ask(self, question: str) -> AgentResponse:
        chunks = self.retriever.retrieve(question, top_k=self.top_k)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": self._build_user_prompt(question, chunks)}],
        )
        raw_text = "".join(block.text for block in message.content if block.type == "text")

        try:
            parsed = self._parse_model_json(raw_text)
            answer = parsed.get("answer", "").strip()
            sources_sufficient = bool(parsed.get("sources_sufficient", False))
            gap_note = parsed.get("gap_note", "")
        except (json.JSONDecodeError, AttributeError):
            # Degrade gracefully: surface the raw text rather than crashing,
            # and flag it clearly as a parse failure so it's never mistaken
            # for a validated, grounded answer.
            answer = raw_text.strip()
            sources_sufficient = False
            gap_note = "Model response could not be parsed as structured JSON."

        grounded, invalid_markers, citations = self._validate_grounding(answer, chunks)

        return AgentResponse(
            question=question,
            answer=answer,
            sources_sufficient=sources_sufficient,
            gap_note=gap_note,
            citations=citations,
            retrieved_chunks=[{"source": c["source"], "score": c["score"]} for c in chunks],
            grounded=grounded,
            ungrounded_markers=invalid_markers,
        )
