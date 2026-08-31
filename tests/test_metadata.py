from rag.pdf_loader import extract_text_from_pdf
from rag.chunker import create_chunks
from rag.metadata import add_metadata


pdf_path = "data/uploads/UNICEF Annual Report 2025.pdf"

pages = extract_text_from_pdf(pdf_path)
chunks = create_chunks(pages)

metadata_chunks = add_metadata(
    chunks,
    "UNICEF Annual Report 2025.pdf"
)

print("Total chunks:", len(metadata_chunks))

for chunk in metadata_chunks[:5]:
    print("\n--- Chunk ---")
    print("Text:", chunk["text"][:100])
    print("Metadata:", chunk["metadata"])


# Metadata verification
chunk_ids = set()

for chunk in metadata_chunks:
    assert chunk["text"].strip() != ""

    metadata = chunk["metadata"]

    assert metadata["document_name"] == "UNICEF Annual Report 2025.pdf"
    assert metadata["page"] >= 1
    assert metadata["chunk_id"] not in chunk_ids

    chunk_ids.add(metadata["chunk_id"])

print("\nMetadata verification passed!")