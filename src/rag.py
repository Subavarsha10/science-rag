
import chromadb
from sentence_transformers import SentenceTransformer
from src.llm import ask_llm

DB_PATH = "vectorstore"
COLLECTION_NAME = "science_ncert"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print("Loading NCERT retrieval system...")

embedding_model = SentenceTransformer(MODEL_NAME)
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(name=COLLECTION_NAME)


def answer_question(question):
    # Convert the question into an embedding
    query_embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True
    ).tolist()

    # Retrieve relevant textbook chunks
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(3, collection.count())
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        return "No relevant textbook content was found."

    context_parts = []

    for document, metadata in zip(documents, metadatas):
        context_parts.append(
            f"Source: {metadata['source']}\n{document}"
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""
Answer the student's question using only the NCERT context below.

If the context does not contain enough information, say so clearly.
Do not invent textbook facts.
Explain the answer in simple Class 10 Science language.

NCERT CONTEXT:
{context}

STUDENT QUESTION:
{question}
"""

    answer = ask_llm(prompt)

    sources = sorted(set(
        metadata["source"] for metadata in metadatas
    ))

    return (
        f"Answer:\n{answer}\n\n"
        f"Sources: {', '.join(sources)}"
    )


if __name__ == "__main__":
    print(f"Loaded {collection.count()} textbook chunks.")

    while True:
        question = input(
            "\nAsk a Class 10 Science question (or type 'exit'): "
        ).strip()

        if question.lower() == "exit":
            print("Goodbye!")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            print("\n" + answer_question(question))
        except Exception as error:
            print(f"Error: {error}")
