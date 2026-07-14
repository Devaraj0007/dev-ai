from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT_DIR / "data" / "questions.txt"


BASE_QUESTIONS = [
    "How many weeks of paid parental leave do employees get once they've completed 12 months of service?",
    "Can an employee work fully remote without any approval?",
    "How many days of PTO do full-time employees accrue per year?",
    "What is the PTO accrual rate for full-time employees?",
    "How many PTO days can employees carry over into the next year?",
    "How long do new hires have to wait before taking PTO?",
    "What exception applies to the first 30 days of employment for PTO?",
    "How much parental leave is available to employees with less than 12 months of service?",
    "Can parental leave be split into multiple blocks?",
    "How long do employees have to submit expense reports?",
    "What approvals are needed for reimbursements over $500?",
    "How quickly are reimbursements processed after approval?",
    "When are performance reviews conducted?",
    "What rating scale is used for performance reviews?",
    "When do compensation adjustments from performance reviews take effect?",
    "What equipment do new employees receive?",
    "How do employees request additional equipment?",
    "How long do employees have to return company equipment after their last day?",
    "What data sources does PulseBoard support?",
    "What is the minimum Docker Engine version required to run PulseBoard?",
    "How much RAM does PulseBoard need for typical workloads?",
    "What deployment mode is recommended for workloads above 200 concurrent viewers?",
    "How often do dashboards refresh by default?",
    "What is the minimum data refresh interval on the Pro plan?",
    "What is the minimum data refresh interval on the Starter plan?",
    "What alert routing options does PulseBoard support?",
    "How many active alerts can a dashboard have on the Starter and Pro plans?",
    "Does the Enterprise plan have an alert limit?",
    "What is the most common cause of a blank PulseBoard dashboard?",
    "How do you fix a blank PulseBoard dashboard?",
    "What is the second most common cause of a blank PulseBoard dashboard?",
    "What usually causes slow PulseBoard load times?",
    "How can slow dashboard load times be improved?",
    "How many tiles on one page start to hurt PulseBoard performance?",
    "What are the available PulseBoard roles?",
    "Which PulseBoard role can manage data sources, users, and billing?",
    "What was Northwind Analytics' total revenue in Q3 2026?",
    "How much did Northwind Analytics' revenue grow year over year in Q3 2026?",
    "How much subscription revenue did Northwind Analytics record in Q3 2026?",
    "How much revenue came from professional services and one-time implementation fees in Q3 2026?",
    "What was North America revenue in Q3 2026?",
    "How fast did North America grow in Q3 2026?",
    "What was EMEA revenue in Q3 2026?",
    "What drove EMEA's growth in Q3 2026?",
    "What was APAC revenue in Q3 2026?",
    "How many paying customers did Northwind Analytics have at the end of Q3 2026?",
    "What was net revenue retention in Q3 2026?",
    "What was gross revenue retention in Q3 2026?",
    "How many customers had annual contract value above $100,000 at the end of Q3 2026?",
    "What was Northwind Analytics' operating margin in Q3 2026?",
    "What drove the improvement in operating margin in Q3 2026?",
    "What is Northwind Analytics' projected revenue range for Q4 2026?",
    "What is Northwind Analytics' full-year 2026 revenue guidance?",
]


LEAD_INS = [
    "Please answer directly",
    "Please answer briefly",
    "Could you answer",
    "Can you confirm from the sources",
    "Help me verify",
    "I need a direct answer to",
    "I'm checking",
    "For reference,",
    "Using only the provided sources,",
    "In plain language,",
    "From the documents,",
    "Based on the sources,",
    "Quick check:",
    "A reviewer needs to know:",
    "For onboarding:",
    "For support:",
    "For the record:",
    "I want to know",
    "Please summarize",
    "Could you clarify",
]


def build_questions() -> list[str]:
    questions: list[str] = [base.strip() for base in BASE_QUESTIONS]
    for lead_in in LEAD_INS:
        for base in BASE_QUESTIONS:
            question = f"{lead_in} {base}" if lead_in.endswith((",", ":")) else f"{lead_in}: {base}"
            questions.append(question)

    seen: set[str] = set()
    deduped: list[str] = []
    for question in questions:
        normalized = question.strip()
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(normalized)
    return deduped


def main() -> None:
    questions = build_questions()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(questions) + "\n", encoding="utf-8")
    print(f"Wrote {len(questions)} questions to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()