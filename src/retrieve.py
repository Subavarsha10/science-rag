
import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = "vectorstore"
COLLECTION_NAME = "science_ncert"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class ScienceRetriever:
    def __init__(self):
        print("Loading embedding model...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        self.client = chromadb.PersistentClient(path=DB_DIR)
        self.collection = self.client.get_collection(
            name=COLLECTION_NAME
        )

        print("Connected to collection:", COLLECTION_NAME)
        print("Total stored chunks:", self.collection.count())

    def search(self, question, n_results=5, source_type=None):
        """
        Search stored NCERT and PYQ chunks.

        source_type:
            "ncert" -> NCERT chunks (including legacy chunks without type)
            "pyq"   -> PYQ chunks only
            None    -> both NCERT and PYQ chunks
        """
        if not question or not question.strip():
            return []

        if source_type is not None:
            source_type = source_type.lower()
            if source_type not in ("ncert", "pyq"):
                raise ValueError(
                    "source_type must be 'ncert', 'pyq', or None"
                )

        total_count = self.collection.count()
        if total_count == 0:
            return []

        query_embedding = self.model.encode(
            [question.strip()],
            normalize_embeddings=True
        ).tolist()

        # Retrieve candidates from the existing collection.
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(total_count, max(n_results * 10, 50)),
            include=["documents", "metadatas", "distances"]
        )

        documents = (results.get("documents") or [[]])[0] or []
        metadatas = (results.get("metadatas") or [[]])[0] or []
        distances = (results.get("distances") or [[]])[0] or []

        matches = []

        for i, document in enumerate(documents):
            metadata = metadatas[i] or {}

            # Original NCERT records have no "type" field.
            item_type = metadata.get("type", "ncert")

            if source_type is not None and item_type != source_type:
                continue

            matches.append({
                "text": document,
                "source": metadata.get("source", "Unknown source"),
                "type": item_type,
                "page": metadata.get("page"),
                "chunk_index": metadata.get("chunk_index"),
                "distance": (
                    distances[i] if i < len(distances) else None
                )
            })

            if len(matches) >= n_results:
                break

        return matches


if __name__ == "__main__":
    retriever = ScienceRetriever()

    question = input("\nEnter a Science question: ").strip()
    source_type = input(
        "Source filter (ncert/pyq/all): "
    ).strip().lower()

    if source_type in ("", "all"):
        source_type = None
    elif source_type not in ("ncert", "pyq"):
        print("Invalid filter. Searching all sources.")
        source_type = None

    results = retriever.search(
        question,
        n_results=5,
        source_type=source_type
    )

    if not results:
        print("\nNo matching content found in the retrieved candidates.")
        print("Try another question or source filter.")
    else:
        for index, result in enumerate(results, start=1):
            print(f"\n--- Result {index} ---")
            print("Type:", result["type"].upper())
            print("Source:", result["source"])

            if result["page"] is not None:
                print("Page:", result["page"])

            if result["distance"] is not None:
                print("Distance:", round(result["distance"], 4))

            print("Text:")
            print(result["text"][:700])
