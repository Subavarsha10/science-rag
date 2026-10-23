
import csv
import time
from pathlib import Path

from src.retrieve import ScienceRetriever
from src.rag import answer_question


# ==================================================
# CONFIGURATION
# ==================================================

OUTPUT_DIR = Path("evaluation")
OUTPUT_FILE = OUTPUT_DIR / "rag_evaluation_results.csv"

TEST_CASES = [
    {
        "id": "NCERT-01",
        "question": "What is photosynthesis?",
        "source_type": "ncert",
        "expected_topic": "photosynthesis",
    },
    {
        "id": "NCERT-02",
        "question": "What is the function of stomata?",
        "source_type": "ncert",
        "expected_topic": "stomata",
    },
    {
        "id": "NCERT-03",
        "question": "What is Ohm's law?",
        "source_type": "ncert",
        "expected_topic": "ohm",
    },
    {
        "id": "NCERT-04",
        "question": "Explain the difference between acids and bases.",
        "source_type": "ncert",
        "expected_topic": "acid",
    },
    {
        "id": "PYQ-01",
        "question": (
            "Find a previous-year question about photosynthesis "
            "from the uploaded CBSE Science papers."
        ),
        "source_type": "pyq",
        "expected_topic": "photosynthesis",
    },
    {
        "id": "PYQ-02",
        "question": (
            "Find a previous-year question about electricity "
            "from the uploaded CBSE Science papers."
        ),
        "source_type": "pyq",
        "expected_topic": "electric",
    },
]


# ==================================================
# HELPERS
# ==================================================

def safe_text(value):
    """Convert a value to a CSV-safe string."""
    if value is None:
        return ""
    return str(value).replace("\n", " ").strip()


def evaluate_retrieval(retriever, test_case):
    """Evaluate whether relevant source material is retrieved."""

    started = time.perf_counter()

    try:
        results = retriever.search(
            test_case["question"],
            n_results=5,
            source_type=test_case["source_type"]
        )

        elapsed = time.perf_counter() - started

        combined_text = " ".join(
            item.get("text", "")
            for item in results
        ).lower()

        expected_topic = test_case["expected_topic"].lower()
        topic_found = expected_topic in combined_text

        correct_type = all(
            item.get("type", "ncert").lower()
            == test_case["source_type"]
            for item in results
        )

        return {
            "retrieval_count": len(results),
            "topic_found": topic_found,
            "correct_source_type": correct_type,
            "retrieval_seconds": round(elapsed, 3),
            "sources": "; ".join(
                item.get("source", "Unknown")
                for item in results
            ),
            "retrieval_status": (
                "PASS"
                if results and topic_found and correct_type
                else "CHECK"
            ),
            "retrieval_error": "",
        }

    except Exception as error:
        return {
            "retrieval_count": 0,
            "topic_found": False,
            "correct_source_type": False,
            "retrieval_seconds": round(
                time.perf_counter() - started, 3
            ),
            "sources": "",
            "retrieval_status": "ERROR",
            "retrieval_error": str(error),
        }


def evaluate_answer(question):
    """Test whether the answer pipeline returns a non-empty answer."""

    started = time.perf_counter()

    try:
        response = answer_question(question)

        if isinstance(response, dict):
            answer = response.get("answer", "")
            sources = response.get("sources", [])
        else:
            answer = str(response)
            sources = []

        elapsed = time.perf_counter() - started

        return {
            "answer_present": bool(answer.strip()),
            "answer_length": len(answer),
            "answer_seconds": round(elapsed, 3),
            "answer_sources": "; ".join(
                (
                    f"{item.get('type', 'UNKNOWN')}:"
                    f"{item.get('source', 'Unknown')}"
                )
                for item in sources
            ),
            "answer_status": (
                "PASS" if answer.strip() else "CHECK"
            ),
            "answer_error": "",
        }

    except Exception as error:
        return {
            "answer_present": False,
            "answer_length": 0,
            "answer_seconds": round(
                time.perf_counter() - started, 3
            ),
            "answer_sources": "",
            "answer_status": "ERROR",
            "answer_error": str(error),
        }


# ==================================================
# MAIN EVALUATION
# ==================================================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("SCIENCE RAG TUTOR — EVALUATION")
    print("=" * 60)

    retriever = ScienceRetriever()
    evaluation_rows = []

    for index, test_case in enumerate(TEST_CASES, start=1):
        print(
            f"\n[{index}/{len(TEST_CASES)}] "
            f"{test_case['id']}: {test_case['question']}"
        )

        retrieval = evaluate_retrieval(retriever, test_case)

        print(
            f"Retrieval: {retrieval['retrieval_status']} | "
            f"Results: {retrieval['retrieval_count']} | "
            f"Topic found: {retrieval['topic_found']}"
        )

        answer = evaluate_answer(test_case["question"])

        print(
            f"Answer: {answer['answer_status']} | "
            f"Length: {answer['answer_length']} characters | "
            f"Time: {answer['answer_seconds']} seconds"
        )

        evaluation_rows.append({
            "test_id": test_case["id"],
            "question": test_case["question"],
            "expected_source_type": test_case["source_type"],
            "expected_topic": test_case["expected_topic"],
            **retrieval,
            **answer,
        })

    # Save detailed results.
    fieldnames = list(evaluation_rows[0].keys())

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(evaluation_rows)

    # Print a summary.
    total = len(evaluation_rows)

    retrieval_passes = sum(
        row["retrieval_status"] == "PASS"
        for row in evaluation_rows
    )

    answer_passes = sum(
        row["answer_status"] == "PASS"
        for row in evaluation_rows
    )

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total test cases: {total}")
    print(
        f"Retrieval checks passed: {retrieval_passes}/{total} "
        f"({retrieval_passes / total * 100:.1f}%)"
    )
    print(
        f"Answer pipeline returned text: {answer_passes}/{total} "
        f"({answer_passes / total * 100:.1f}%)"
    )
    print(f"\nDetailed results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
