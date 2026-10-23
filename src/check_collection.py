
import chromadb
from collections import Counter

client = chromadb.PersistentClient(path="vectorstore")
collection = client.get_collection(name="science_ncert")

print("Total chunks:", collection.count())

data = collection.get(
    limit=20,
    include=["metadatas"]
)

print("\nMetadata from first 20 chunks:")
for metadata in data["metadatas"]:
    print(metadata)

all_data = collection.get(include=["metadatas"])
types = Counter(
    (metadata or {}).get("type", "MISSING")
    for metadata in all_data["metadatas"]
)

print("\nCounts by type:")
print(types)
