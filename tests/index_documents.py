import os

from rag.pdf_loader import extract_text_from_pdf
from rag.chunker import create_chunks
from rag.metadata import add_metadata
from rag.embeddings import generate_embeddings
from rag.vector_store import get_vector_store, add_documents


UPLOAD_DIR = "data/uploads"

collection = get_vector_store()


for filename in os.listdir(UPLOAD_DIR):

    if not filename.lower().endswith(".pdf"):
        continue

    # Check whether this PDF is already indexed
    existing = collection.get(
        where={"document_name": filename}
    )

    if existing["ids"]:
        print(f"\nSkipping already indexed: {filename}")
        continue

    pdf_path = os.path.join(UPLOAD_DIR, filename)

    print(f"\nProcessing: {filename}")

    # Extract PDF text
    pages = extract_text_from_pdf(pdf_path)

    # Create chunks
    chunks = create_chunks(pages)

    # Add metadata
    metadata_chunks = add_metadata(
        chunks,
        filename
    )

    print("Pages:", len(pages))
    print("Chunks:", len(metadata_chunks))

    # Prepare data
    documents = [chunk["text"] for chunk in metadata_chunks]
    metadatas = [chunk["metadata"] for chunk in metadata_chunks]
    ids = [metadata["chunk_id"] for metadata in metadatas]

    # Make IDs unique across different PDFs
    ids = [
        f"{filename}_{chunk_id}"
        for chunk_id in ids
    ]

    print("Generating embeddings...")

    embeddings = generate_embeddings(documents)

    print("Embeddings generated:", len(embeddings))

    # Store in ChromaDB
    add_documents(
        collection,
        documents,
        embeddings,
        metadatas,
        ids
    )

    print(f"Successfully indexed: {filename}")


print("\n================================")
print("Indexing complete!")
print("Documents in ChromaDB:", collection.count())
print("================================")