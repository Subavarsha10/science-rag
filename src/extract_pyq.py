
import pathlib
import pymupdf

folder = pathlib.Path("data/raw/pyq")
pdfs = sorted(folder.rglob("*.pdf"))

if not pdfs:
    print("No PDFs found.")
else:
    pdf = pdfs[0]
    print("Checking:", pdf.name)

    with pymupdf.open(pdf) as doc:
        for page_num, page in enumerate(doc[:2], start=1):
            text = page.get_text("text", sort=True)
            print(f"\n--- Page {page_num} ---")
            print(text[:3000])
