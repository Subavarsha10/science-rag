
from pathlib import Path
import pymupdf

INPUT_DIR = Path("data/raw/pyq")
OUTPUT_DIR = Path("data/processed/pyq_english_ocr")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

pdf_files = sorted(INPUT_DIR.rglob("*.pdf"))

if not pdf_files:
    print("No PDF files found in", INPUT_DIR)
    raise SystemExit(1)

for pdf_path in pdf_files:
    print(f"\nProcessing: {pdf_path.name}")
    page_texts = []

    with pymupdf.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            # OCR the rendered page using English recognition.
            text_page = page.get_textpage_ocr(
                language="eng",
                dpi=250,
                full=True
            )
            text = page.get_text("text", textpage=text_page, sort=True)
            page_texts.append(
                f"\n--- Page {page_number} ---\n{text.strip()}"
            )

    output_path = OUTPUT_DIR / f"{pdf_path.stem}.txt"
    output_path.write_text("\n".join(page_texts), encoding="utf-8")
    print(f"Saved: {output_path}")

print("\nOCR extraction completed.")
