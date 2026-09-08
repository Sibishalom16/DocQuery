def add_metadata(chunks, document_name, document_id, user_id):
    metadata_chunks = []

    for index, chunk in enumerate(chunks, start=1):
        metadata_chunks.append({
            "text": chunk["text"],
            "metadata": {
                "document_id": document_id,
                "user_id": user_id,
                "document_name": document_name,
                "page": chunk["page"],
                "chunk_id": f"chunk_{index:04d}"
            }
        })

    return metadata_chunks