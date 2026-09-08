from rag.pdf_loader import extract_text_from_pdf
from rag.chunker import create_chunks
from rag.metadata import add_metadata
from rag.embeddings import generate_embeddings
from rag.vector_store import get_vector_store, add_documents


def process_document(file_path, filename, document_id, user_id):
    # Extract text from PDF
    pages = extract_text_from_pdf(file_path)

    # Create chunks
    chunks = create_chunks(pages)

    # Add metadata
    metadata_chunks = add_metadata(
        chunks,
        filename,
        document_id,
        user_id
    )

    # Prepare data
    documents = [
        chunk["text"]
        for chunk in metadata_chunks
    ]

    metadatas = [
        chunk["metadata"]
        for chunk in metadata_chunks
    ]

    ids = [
        f"{document_id}_{metadata['chunk_id']}"
        for metadata in metadatas
    ]

    # Generate embeddings
    embeddings = generate_embeddings(documents)

    # Store in ChromaDB
    collection = get_vector_store()

    add_documents(
        collection,
        documents,
        embeddings,
        metadatas,
        ids
    )

    return {
        "pages": len(pages),
        "chunks": len(documents)
    }