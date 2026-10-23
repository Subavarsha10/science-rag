
import json
import pathlib
from langchain_text_splitters import RecursiveCharacterTextSplitter

input_dir = pathlib.Path("data/processed")
output_dir = pathlib.Path("data/chunks")
output_dir.mkdir(parents=True, exist_ok=True)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)

markdown_files = sorted(input_dir.glob("*.md"))

if not markdown_files:
    print("No Markdown files found in data/processed.")
else:
    all_chunks = []

    for file_path in markdown_files:
        text = file_path.read_text(encoding="utf-8")
        chunks = splitter.split_text(text)

        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{file_path.stem}_{index}",
                "source": file_path.name,
                "chunk_index": index,
                "text": chunk
            })

        print(f"{file_path.name}: {len(chunks)} chunks")

    output_file = output_dir / "chunks.json"
    output_file.write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Saved to: {output_file}")
