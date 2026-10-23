
import re

from src.retrieve import ScienceRetriever
from src.llm import ask_llm


# Initialize the retriever once.
retriever = ScienceRetriever()


def detect_question_intent(question):
    """
    Return 'pyq' for previous-year question requests.
    Otherwise, prioritize NCERT for topic/concept questions.
    """
    text = question.lower()

    pyq_patterns = [
        r"\bpyq\b",
        r"\bprevious[\s-]*year questions?\b",
        r"\bpast[\s-]*year questions?\b",
        r"\bpast exam questions?\b",
        r"\bprevious exam questions?\b",
        r"\bboard exam questions?\b",
        r"\bquestions? from (?:the )?(?:previous|past) years?\b",
        r"\bquestion paper\b",
        r"\bsample paper questions?\b",
        r"\bquestions? asked in (?:the )?(?:board )?exam\b",
    ]

    if any(re.search(pattern, text) for pattern in pyq_patterns):
        return "pyq"

    return "ncert"


def _search_source(question, source_type, n_results):
    """Retrieve chunks from one source type."""
    try:
        return retriever.search(
            question,
            n_results=n_results,
            source_type=source_type
        )
    except Exception as error:
        # Avoid silently hiding unexpected retrieval errors.
        raise RuntimeError(
            f"Could not retrieve {source_type.upper()} content: {error}"
        ) from error


def _format_source(result):
    """Create a unique source record for the UI."""
    source = {
        "type": str(result.get("type", "ncert")).upper(),
        "source": result.get("source", "Unknown source"),
        "page": result.get("page")
    }
    return source


def answer_question(question):
    question = question.strip()

    if not question:
        return {
            "answer": "Please enter a Science question.",
            "sources": []
        }

    intent = detect_question_intent(question)

    # Prioritize the requested source type.
    primary_type = "pyq" if intent == "pyq" else "ncert"
    secondary_type = "ncert" if primary_type == "pyq" else "pyq"

    primary_results = _search_source(
        question,
        source_type=primary_type,
        n_results=4
    )

    secondary_results = _search_source(
        question,
        source_type=secondary_type,
        n_results=2
    )

    # Keep the requested source first in the context.
    results = primary_results + secondary_results

    if not results:
        return {
            "answer": (
                "I couldn't find relevant content in the available "
                "NCERT textbook or PYQ collection. Try rephrasing "
                "your question or asking about a specific Class 10 "
                "Science topic."
            ),
            "sources": []
        }

    context_parts = []
    sources = []
    seen_sources = set()

    for result in results:
        source = _format_source(result)

        citation = f"{source['type']}: {source['source']}"
        if source["page"] is not None:
            citation += f", page {source['page']}"

        context_parts.append(
            f"[Source: {citation}]\n{result['text']}"
        )

        source_key = (
            source["type"],
            source["source"],
            source["page"]
        )

        if source_key not in seen_sources:
            sources.append(source)
            seen_sources.add(source_key)

    context = "\n\n".join(context_parts)

    if intent == "pyq":
        task_instruction = """
The student explicitly requested a previous-year or exam question.

- Prioritize the retrieved PYQ material.
- If the context contains an actual question, reproduce or summarize
  it faithfully and identify its source.
- If the student asks for an answer or explanation, use NCERT context
  as supporting information.
- Never invent a past exam question or claim that a question appeared
  in an exam unless the supplied PYQ context supports that claim.
- If no actual relevant PYQ is present in the retrieved context,
  clearly say that a matching question was not found. You may explain
  the topic using NCERT context, but label it as an explanation,
  not as a verified PYQ.
"""
    else:
        task_instruction = """
The student is asking a topic or concept question.

- Prioritize NCERT content for the explanation.
- Use PYQ material only as supporting context or an example when relevant.
- Do not present a PYQ as textbook content.
- If the retrieved context is insufficient, state the limitation honestly.
"""

    prompt = f"""
You are a helpful Class 10 Science tutor.

{task_instruction}

General rules:
- Answer at Class 10 level using clear, accurate explanations.
- Use the supplied context as your primary evidence.
- Do not invent citations, page numbers, or exam history.
- Distinguish textbook content from previous-year questions.
- If the context does not support a claim, do not present it as verified.
- Write chemical equations clearly and balance them when appropriate.

Retrieved context:
{context}

Student question:
{question}

Provide the answer now.
"""

    answer = ask_llm(prompt)

    return {
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":
    question = input("Enter a Science question: ").strip()
    response = answer_question(question)

    print("\nAnswer:\n")
    print(response["answer"])

    print("\nSources:")
    for source in response["sources"]:
        details = f"- [{source['type']}] {source['source']}"
        if source["page"] is not None:
            details += f" (page {source['page']})"
        print(details)
