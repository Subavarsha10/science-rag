
import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = Path("data/chunks/pyq_chunks.json")
DB_DIR = "vectorstore"
COLLECTION_NAME = "science_ncert"
BATCH_SIZE = 100

if not CHUNKS_FILE.exists():
    raise FileNotFoundError(
        f"{CHUNKS_FILE} not found. Run src/chunk_pyq_ocr.py first."
    )

with CHUNKS_FILE.open("r", encoding="utf-8") as f:
    chunks = json.load(f)

if not chunks:
    raise ValueError("No PYQ chunks found.")

# Validate the input before modifying Chroma.
required_fields = {"id", "text", "source", "page", "chunk_index"}

for index, item in enumerate(chunks):
    missing = required_fields - item.keys()
    if missing:
        raise ValueError(
            f"Chunk {index} is missing fields: {sorted(missing)}"
        )
    if not item["text"].strip():
        raise ValueError(f"Chunk {index} has empty text.")

ids_in_file = [item["id"] for item in chunks]
if len(ids_in_file) != len(set(ids_in_file)):
    raise ValueError("Duplicate IDs found in PYQ chunks.")

print("Loading the existing embedding model...")
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=DB_DIR)

# Do NOT delete or recreate this collection.
collection = client.get_collection(name=COLLECTION_NAME)

print("Existing collection:", COLLECTION_NAME)
print("Existing stored chunks:", collection.count())

added = 0
skipped = 0

for start in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[start:start + BATCH_SIZE]

    batch_ids = [item["id"] for item in batch]

    # Skip IDs already stored so rerunning is safe.
    existing = set(collection.get(ids=batch_ids)["ids"])
    new_items = [
        item for item in batch if item["id"] not in existing
    ]

    skipped += len(batch) - len(new_items)

    if not new_items:
        continue

    texts = [item["text"] for item in new_items]
    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    ).tolist()

    collection.add(
        ids=[item["id"] for item in new_items],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "source": item["source"],
                "type": "pyq",
                "page": int(item["page"]),
                "chunk_index": int(item["chunk_index"])
            }
            for item in new_items
        ]
    )

    added += len(new_items)
    print(f"Added {added} new PYQ chunks so far.")

print("\nPYQ integration completed.")
print("New chunks added:", added)
print("Existing IDs skipped:", skipped)
print("Total chunks in collection:", collection.count())
