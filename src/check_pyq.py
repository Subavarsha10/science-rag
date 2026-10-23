
import pathlib

try:
    import pymupdf
except ImportError:
    print("PyMuPDF is missing. Install it using:")
    print("python -m pip install pymupdf")
    raise SystemExit(1)

folder = pathlib.Path("data/raw/pyq")
pdfs = sorted(folder.rglob("*.pdf"))

if not pdfs:
    print("No PDF files found in data/raw/pyq")
    raise SystemExit(1)

pdf = pdfs[0]
print("Checking PDF:", pdf.name)

with pymupdf.open(pdf) as doc:
    for page_num, page in enumerate(doc[:2], start=1):
        text = page.get_text("text", sort=True)
        print(f"\n--- Page {page_num} ---")
        print(text[:2500])
