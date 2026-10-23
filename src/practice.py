
import json
import re

from src.retrieve import ScienceRetriever
from src.llm import ask_llm


retriever = ScienceRetriever()


def generate_practice_questions(topic, difficulty="mixed", count=5):
    topic = topic.strip()

    if not topic:
        return {
            "questions": [],
            "error": "Please enter a Science topic."
        }

    if difficulty not in ("easy", "medium", "hard", "mixed"):
        difficulty = "mixed"

    count = max(1, min(int(count), 10))

    # Use NCERT as the primary source for practice questions.
    results = retriever.search(
        topic,
        n_results=5,
        source_type="ncert"
    )

    if not results:
        return {
            "questions": [],
            "error": (
                "No relevant NCERT content was retrieved for this topic. "
                "Try a more specific Class 10 Science topic."
            )
        }

    context = "\n\n".join(
        f"[Source: {item['source']}]\n{item['text']}"
        for item in results
    )

    prompt = f"""
You are a Class 10 CBSE Science teacher.

Generate exactly {count} original practice questions on:
{topic}

Requested difficulty: {difficulty}

Use the supplied NCERT context as the factual basis. Do not claim that
generated questions appeared in previous-year examinations.

Requirements:
- Keep questions appropriate for Class 10 Science.
- Use a suitable mix of MCQs, short-answer and application questions
  when difficulty is mixed.
- Include a correct answer and a brief explanation for each question.
- Avoid duplicates.
- If the supplied context does not support the topic, say so instead
  of inventing unsupported facts.

Return ONLY a valid JSON array. Each element must have:
{{
  "question": "Question text",
  "type": "MCQ, short answer, or application",
  "difficulty": "easy, medium, or hard",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "Correct answer",
  "explanation": "Brief explanation"
}}

For non-MCQ questions, use an empty options array.

NCERT context:
{context}
"""

    response = ask_llm(prompt)

    # Parse JSON returned by the LLM.
    try:
        cleaned = response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        questions = json.loads(cleaned)

        if not isinstance(questions, list):
            raise ValueError("Expected a JSON array.")

        return {
            "questions": questions[:count],
            "sources": [
                {
                    "type": item.get("type", "ncert").upper(),
                    "source": item.get("source", "Unknown source"),
                    "page": item.get("page")
                }
                for item in results
            ],
            "error": None
        }

    except (json.JSONDecodeError, ValueError):
        return {
            "questions": [],
            "error": (
                "The model returned an unexpected format. "
                "Please try generating the questions again."
            )
        }


if __name__ == "__main__":
    topic = input("Enter a Science topic: ").strip()
    difficulty = input(
        "Difficulty (easy/medium/hard/mixed): "
    ).strip().lower() or "mixed"

    result = generate_practice_questions(topic, difficulty, count=5)

    if result.get("error"):
        print(result["error"])
    else:
        for index, question in enumerate(result["questions"], start=1):
            print(f"\n{index}. {question['question']}")
            print("Difficulty:", question.get("difficulty"))
            if question.get("options"):
                print("\n".join(question["options"]))
            print("Answer:", question.get("answer"))
            print("Explanation:", question.get("explanation"))
