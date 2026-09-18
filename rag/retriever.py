from rag.embeddings import generate_embedding
from rag.vector_store import get_vector_store, search_documents


def retrieve_documents(query, user_id, document_id, top_k=20):
    """Retrieve the most relevant document chunks for a query, isolated by user and document."""

    query_embedding = generate_embedding(query)

    collection = get_vector_store()

    # Pass where filter based on ChromaDB requirements
    where_filter = {
        "$and": [
            {"user_id": {"$eq": user_id}},
            {"document_id": {"$eq": document_id}}
        ]
    }

    results = search_documents(
        collection,
        query_embedding,
        top_k=top_k,
        where=where_filter
    )


    retrieved_documents = []

    for i in range(len(results["documents"][0])):
        retrieved_documents.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return retrieved_documents