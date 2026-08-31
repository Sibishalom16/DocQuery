from rag.pdf_loader import extract_text_from_pdf
from rag.chunker import create_chunks
from rag.metadata import add_metadata
from rag.embeddings import generate_embeddings
from rag.vector_store import get_vector_store, add_documents


PDF_PATH = "data/uploads/UNICEF Annual Report 2025.pdf"
DOCUMENT_NAME = "UNICEF Annual Report 2025.pdf"


# Extract PDF text
pages = extract_text_from_pdf(PDF_PATH)

# Create chunks
chunks = create_chunks(pages)

# Add metadata
metadata_chunks = add_metadata(
    chunks,
    DOCUMENT_NAME
)

print("Pages:", len(pages))
print("Chunks:", len(metadata_chunks))


# Prepare data for embedding
documents = [chunk["text"] for chunk in metadata_chunks]
metadatas = [chunk["metadata"] for chunk in metadata_chunks]
ids = [metadata["chunk_id"] for metadata in metadatas]


# Generate Gemini embeddings
print("Generating embeddings...")

embeddings = generate_embeddings(documents)

print("Embeddings generated:", len(embeddings))


# Store everything in ChromaDB
collection = get_vector_store()

add_documents(
    collection,
    documents,
    embeddings,
    metadatas,
    ids
)

print("Successfully indexed documents!")
print("Documents in ChromaDB:", collection.count())
