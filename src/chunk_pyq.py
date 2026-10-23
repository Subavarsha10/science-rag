
from pathlib import Path
import pymupdf

folder = Path("data/raw/pyq")
pdfs = sorted(folder.rglob("*.pdf"))

if not pdfs:
    print("No PDFs found.")
    raise SystemExit(1)

pdf = pdfs[0]
print("Checking:", pdf.name)

with pymupdf.open(pdf) as doc:
    page = doc[0]
    words = page.get_text("words", sort=True)

    for word in words[:100]:
        x0, y0, x1, y1, text = word[:5]
        print(repr(text))
