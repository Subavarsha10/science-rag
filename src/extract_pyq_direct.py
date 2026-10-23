
from pathlib import Path
import pymupdf

input_folder = Path("data/raw/pyq")
output_folder = Path("data/processed/pyq_english")
output_folder.mkdir(parents=True, exist_ok=True)

pdf_files = sorted(input_folder.rglob("*.pdf"))

if not pdf_files:
    print("No PDF files found in data/raw/pyq")
    raise SystemExit(1)

for pdf_path in pdf_files:
    print(f"Processing: {pdf_path.name}")

    pages_text = []

    with pymupdf.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text("text", sort=True)

            # Keep only lines containing English letters.
            english_lines = []
            for line in text.splitlines():
                if any("A" <= char <= "Z" or "a" <= char <= "z"
                       for char in line):
                    english_lines.append(line.strip())

            if english_lines:
                pages_text.append(
                    f"\n--- Page {page_number} ---\n"
                    + "\n".join(english_lines)
                )

    output_path = output_folder / f"{pdf_path.stem}.txt"
    output_path.write_text(
        "\n".join(pages_text),
        encoding="utf-8"
    )

    print(f"Saved: {output_path}")

print("\nExtraction completed.")
