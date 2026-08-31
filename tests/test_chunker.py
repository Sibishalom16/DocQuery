from rag.pdf_loader import extract_text_from_pdf
from rag.chunker import create_chunks


pdf_path = "data/uploads/UNICEF Annual Report 2025.pdf"

pages = extract_text_from_pdf(pdf_path)

chunks = create_chunks(pages)

print("Total pages:", len(pages))
print("Total chunks:", len(chunks))

for i, chunk in enumerate(chunks, start=1):
    assert chunk["text"].strip() != ""
    assert len(chunk["text"]) <= 800
    assert chunk["page"] >= 1

print("\nChunking verification passed!")