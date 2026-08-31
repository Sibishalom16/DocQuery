from rag.embeddings import generate_embedding
from rag.vector_store import get_vector_store, search_documents


def retrieve_documents(query, top_k=5):
    """Retrieve the most relevant document chunks for a query."""

    query_embedding = generate_embedding(query)

    collection = get_vector_store()

    results = search_documents(
        collection,
        query_embedding,
        top_k=top_k
    )

    retrieved_documents = []

    for i in range(len(results["documents"][0])):
        retrieved_documents.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return retrieved_documents