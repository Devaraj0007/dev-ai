"""
cli.py
Command-line entrypoint for the Research Agent.

Usage:
    python -m src.cli ingest
    python -m src.cli ask "What is the parental leave policy?"
    python -m src.cli batch questions.txt --out outputs/sample_qa.json
    python -m src.cli interactive
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from src.ingest import build_index, DEFAULT_SOURCE_DIR, DEFAULT_INDEX_PATH  # noqa: E402


def cmd_ingest(args):
    stats = build_index(source_dir=args.source_dir, index_path=args.index_path)
    print(f"Indexed {stats['num_chunks']} chunks from {stats['num_documents']} documents.")
    print(f"Saved index to {stats['index_path']}")


def cmd_ask(args):
    from src.agent import ResearchAgent  # deferred import: avoids requiring an API key for `ingest`

    agent = ResearchAgent(top_k=args.top_k)
    response = agent.ask(args.question)
    _print_response(response)


def cmd_batch(args):
    from src.agent import ResearchAgent

    if not os.path.exists(args.questions_file):
        print(f"Questions file not found: {args.questions_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.questions_file, "r", encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    agent = ResearchAgent(top_k=args.top_k)
    results = []
    for i, q in enumerate(questions, start=1):
        print(f"[{i}/{len(questions)}] {q}")
        response = agent.ask(q)
        results.append(response.to_dict())
        _print_response(response, indent=True)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} results to {args.out}")


def cmd_interactive(args):
    from src.agent import ResearchAgent

    agent = ResearchAgent(top_k=args.top_k)
    print("Research Agent (interactive). Type 'exit' to quit.\n")
    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue
        response = agent.ask(question)
        _print_response(response)


def _print_response(response, indent: bool = False):
    pad = "  " if indent else ""
    print(f"{pad}Answer: {response.answer}")
    print(f"{pad}Sources sufficient: {response.sources_sufficient}")
    if response.gap_note:
        print(f"{pad}Gap note: {response.gap_note}")
    print(f"{pad}Grounded: {response.grounded}" + (f" (invalid markers: {response.ungrounded_markers})" if not response.grounded else ""))
    for c in response.citations:
        print(f"{pad}  {c['marker']} -> {c['source']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Research Agent with Citations")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Build the retrieval index from data/sources")
    p_ingest.add_argument("--source-dir", default=DEFAULT_SOURCE_DIR)
    p_ingest.add_argument("--index-path", default=DEFAULT_INDEX_PATH)
    p_ingest.set_defaults(func=cmd_ingest)

    p_ask = sub.add_parser("ask", help="Ask a single question")
    p_ask.add_argument("question", type=str)
    p_ask.add_argument("--top-k", type=int, default=4)
    p_ask.set_defaults(func=cmd_ask)

    p_batch = sub.add_parser("batch", help="Run a newline-separated file of questions")
    p_batch.add_argument("questions_file", type=str)
    p_batch.add_argument("--out", type=str, default="outputs/sample_qa.json")
    p_batch.add_argument("--top-k", type=int, default=4)
    p_batch.set_defaults(func=cmd_batch)

    p_interactive = sub.add_parser("interactive", help="Interactive Q&A loop")
    p_interactive.add_argument("--top-k", type=int, default=4)
    p_interactive.set_defaults(func=cmd_interactive)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
