import chromadb


def get_vector_store():
    """Create and return a persistent ChromaDB collection."""
    client = chromadb.PersistentClient(path="data/chroma")

    collection = client.get_or_create_collection(
        name="documents"
    )

    return collection


def add_documents(collection, documents, embeddings, metadatas, ids):
    """Add document chunks and their embeddings to ChromaDB."""
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )


def search_documents(collection, query_embedding, top_k=5):
    """Search ChromaDB for the most similar documents."""
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results