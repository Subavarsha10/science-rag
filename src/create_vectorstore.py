
import json
import pathlib
import chromadb
from sentence_transformers import SentenceTransformer

chunks_file = pathlib.Path("data/chunks/chunks.json")
db_dir = "vectorstore"
collection_name = "science_ncert"

if not chunks_file.exists():
    raise FileNotFoundError(
        "chunks.json not found. Run src/chunk_text.py first."
    )

with chunks_file.open("r", encoding="utf-8") as f:
    chunks = json.load(f)

if not chunks:
    raise ValueError("No chunks found in chunks.json.")

print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=db_dir)

# Recreate the collection to avoid duplicate entries on reruns.
try:
    client.delete_collection(collection_name)
except Exception:
    pass

collection = client.create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"}
)

batch_size = 100

for start in range(0, len(chunks), batch_size):
    batch = chunks[start:start + batch_size]

    texts = [item["text"] for item in batch]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()

    collection.add(
        ids=[item["chunk_id"] for item in batch],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "source": item["source"],
                "chunk_index": item["chunk_index"]
            }
            for item in batch
        ]
    )

    print(f"Stored {min(start + batch_size, len(chunks))}/{len(chunks)} chunks")

print("Vector database created successfully!")
print("Total stored chunks:", collection.count())
print("Database folder:", db_dir)
