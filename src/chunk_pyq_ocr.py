
import json
import re
from pathlib import Path

INPUT_DIR = Path("data/processed/pyq_english_ocr")
OUTPUT_FILE = Path("data/chunks/pyq_chunks.json")

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def split_into_chunks(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))

        if end < len(text):
            # Prefer ending at a paragraph or line boundary.
            boundary = text.rfind("\n", start, end)
            if boundary > start + CHUNK_SIZE // 2:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(start + 1, end - CHUNK_OVERLAP)

    return chunks


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pdf_text_files = sorted(INPUT_DIR.glob("*.txt"))

    if not pdf_text_files:
        print(f"No OCR text files found in {INPUT_DIR}")
        return

    documents = []

    for file_path in pdf_text_files:
        text = file_path.read_text(encoding="utf-8", errors="replace")

        # Separate the text by the page markers created by the OCR script.
        pages = re.split(r"--- Page (\d+) ---", text)

        for i in range(1, len(pages), 2):
            page_number = int(pages[i])
            page_text = pages[i + 1].strip()

            for chunk_index, chunk in enumerate(
                split_into_chunks(page_text)
            ):
                documents.append({
                    "id": (
                        f"pyq_{file_path.stem}"
                        f"_p{page_number}_c{chunk_index}"
                    ),
                    "text": chunk,
                    "source": file_path.name,
                    "type": "pyq",
                    "page": page_number,
                    "chunk_index": chunk_index
                })

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    print(f"Text files processed: {len(pdf_text_files)}")
    print(f"Chunks created: {len(documents)}")
    print(f"Saved to: {OUTPUT_FILE}")

    if documents:
        print("\nSample chunk:\n")
        print(documents[0]["text"][:1000])


if __name__ == "__main__":
    main()
