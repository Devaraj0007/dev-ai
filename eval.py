"""
eval.py
Lightweight evaluation over a batch output file (outputs/sample_qa.json).
No external eval framework -- just the checks a reviewer would want to see:
  - Does every answer that claims sufficiency actually carry a citation?
  - Are all citation markers grounded (i.e. reference a real retrieved chunk)?
  - How often does the agent correctly flag "not enough information"?

Usage:
    python eval.py [path/to/sample_qa.json]
"""

import json
import re
import sys


def evaluate(path: str):
    with open(path, "r", encoding="utf-8") as f:
        results = json.load(f)

    total = len(results)
    grounded_count = 0
    cited_when_sufficient = 0
    sufficient_count = 0
    insufficient_count = 0
    zero_citation_but_sufficient = []

    for r in results:
        if r["grounded"]:
            grounded_count += 1

        has_citation = bool(re.search(r"\[\d+\]", r["answer"]))
        if r["sources_sufficient"]:
            sufficient_count += 1
            if has_citation:
                cited_when_sufficient += 1
            else:
                zero_citation_but_sufficient.append(r["question"])
        else:
            insufficient_count += 1

    print(f"Total questions evaluated: {total}")
    print(f"Grounded (no invented citation numbers): {grounded_count}/{total}")
    print(f"Flagged as 'insufficient sources': {insufficient_count}/{total}")
    print(
        f"Marked sufficient AND carries at least one citation: "
        f"{cited_when_sufficient}/{sufficient_count if sufficient_count else 0}"
    )
    if zero_citation_but_sufficient:
        print("\nWARNING -- marked sufficient but has no citation marker:")
        for q in zero_citation_but_sufficient:
            print(f"  - {q}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "outputs/sample_qa.json"
    evaluate(path)
