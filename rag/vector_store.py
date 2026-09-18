import chromadb


def get_vector_store():
    """Create and return a persistent ChromaDB collection."""
    client = chromadb.PersistentClient(path="data/chroma")

    collection = client.get_or_create_collection(
        name="documents"
    )

    return collection


def add_documents(collection, documents, embeddings, metadatas, ids):
    """Add (or update) document chunks and their embeddings in ChromaDB.
    Uses upsert so re-uploading a document never raises a duplicate-ID error."""
    collection.upsert(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )



def search_documents(collection, query_embedding, top_k=20, where=None):
    """Search ChromaDB for the most similar documents applying specified filters."""
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where
    )

    return results


def delete_documents(collection, ids):
    """Delete document chunks from ChromaDB."""
    collection.delete(ids=ids)