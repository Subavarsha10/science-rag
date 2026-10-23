
import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = "vectorstore"
COLLECTION_NAME = "science_ncert"

print("Loading embedding model...")
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_collection(name=COLLECTION_NAME)

query = "Explain the process of photosynthesis and write its chemical equation."
query_embedding = model.encode(
    [query],
    normalize_embeddings=True
).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=3,
    where={"type": "pyq"},
    include=["documents", "metadatas", "distances"]
)

print("\nQuery:", query)
print("PYQ results found:", len(results["ids"][0]))

for i, doc_id in enumerate(results["ids"][0]):
    metadata = results["metadatas"][0][i]
    document = results["documents"][0][i]
    distance = results["distances"][0][i]

    print(f"\n--- Result {i + 1} ---")
    print("ID:", doc_id)
    print("Source:", metadata.get("source"))
    print("Page:", metadata.get("page"))
    print("Distance:", round(distance, 4))
    print("Text:", document[:600])

if not results["ids"][0]:
    print("No PYQ chunks found for this query.")
