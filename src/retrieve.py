
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "vectorstore"
COLLECTION_NAME = "science_ncert"

print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(name=COLLECTION_NAME)

print(f"Database loaded. Total chunks: {collection.count()}")

while True:
    question = input("\nAsk a Science question (or type 'exit'): ").strip()

    if question.lower() == "exit":
        print("Exiting retrieval test.")
        break

    if not question:
        print("Please enter a question.")
        continue

    query_embedding = model.encode(
        [question],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(3, collection.count())
    )

    print("\nRelevant textbook content:\n")

    for i, (document, metadata, distance) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ),
        start=1
    ):
        print(f"--- Result {i} ---")
        print(f"Source: {metadata['source']}")
        print(f"Distance: {distance:.4f}")
        print(document[:1000])
        print()
