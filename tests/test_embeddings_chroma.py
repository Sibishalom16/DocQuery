from rag.pdf_loader import extract_text_from_pdf
from rag.chunker import create_chunks
from rag.metadata import add_metadata
from rag.embeddings import generate_embeddings
from rag.vector_store import get_vector_store, add_documents


pdf_path = "data/uploads/UNICEF Annual Report 2025.pdf"

# 1. Extract PDF text
pages = extract_text_from_pdf(pdf_path)

# 2. Create chunks
chunks = create_chunks(pages)

# 3. Add metadata
metadata_chunks = add_metadata(
    chunks,
    "UNICEF Annual Report 2025.pdf"
)

# Use a small number first for testing
metadata_chunks = metadata_chunks[:5]

# 4. Get chunk text
documents = [chunk["text"] for chunk in metadata_chunks]

# 5. Generate Gemini embeddings
embeddings = generate_embeddings(documents)

# 6. Get metadata
metadatas = [chunk["metadata"] for chunk in metadata_chunks]

# 7. Create unique IDs
ids = [metadata["chunk_id"] for metadata in metadatas]

# 8. Connect to ChromaDB
collection = get_vector_store()

# 9. Store chunks + embeddings + metadata
add_documents(
    collection,
    documents,
    embeddings,
    metadatas,
    ids
)

print("Successfully stored chunks in ChromaDB!")
print("Documents in ChromaDB:", collection.count())

assert collection.count() >= 5
