from pathlib import Path
from rag.pdf_loader import extract_text_from_pdf

upload_folder = Path("data/uploads")

for pdf_file in upload_folder.glob("*.pdf"):
    pages = extract_text_from_pdf(pdf_file)

    print(f"\n{pdf_file.name}")
    print(f"Total pages: {len(pages)}")
    print(f"Page 1 characters: {len(pages[0]['text'])}")