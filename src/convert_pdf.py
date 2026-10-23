
import pathlib
import pymupdf4llm

src_dir = pathlib.Path("data/raw/ncert")
out_dir = pathlib.Path("data/processed")

out_dir.mkdir(parents=True, exist_ok=True)

pdf_files = sorted(src_dir.rglob("*.pdf"))

if not pdf_files:
    print("No PDF files found. Check the ncert folder.")
else:
    for pdf in pdf_files:
        print(f"Converting: {pdf.name}")

        try:
            md = pymupdf4llm.to_markdown(str(pdf))

            output_file = out_dir / f"{pdf.stem}.md"
            output_file.write_text(md, encoding="utf-8")

            print(f"Saved: {output_file.name} ({len(md)} characters)")

        except Exception as error:
            print(f"Failed to convert {pdf.name}: {error}")

    print("Conversion process finished.")
