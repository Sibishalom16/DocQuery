from rag.retriever import retrieve_documents
from rag.generator import generate_answer


question = "How many outreach activities did ICSID conduct in 2025?"
# Retrieve relevant chunks
retrieved_documents = retrieve_documents(question, top_k=5)

print("\n--- Retrieved Documents ---")

for i, document in enumerate(retrieved_documents, start=1):
    metadata = document["metadata"]

    print(f"\nChunk {i}")
    print("Page:", metadata.get("page"))
    print("Document:", metadata.get("document_name"))
    print("Distance:", document["distance"])
    print("Text:", document["text"][:300])


# Generate answer using retrieved chunks
answer = generate_answer(
    question,
    retrieved_documents
)

print("\n--- Gemini Answer ---")
print(answer)


# Display sources
print("\n--- Sources ---")

seen_sources = set()

for document in retrieved_documents:
    metadata = document["metadata"]

    document_name = metadata.get("document_name")
    page = metadata.get("page")

    source = (document_name, page)

    if source not in seen_sources:
        print(f"- {document_name} — Page {page}")
        seen_sources.add(source)