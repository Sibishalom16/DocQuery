from rag.generator import generate_answer


question = "What is the purpose of UNICEF?"

retrieved_documents = [
    {
        "text": "UNICEF works to protect the rights of every child and help children survive, thrive and fulfil their potential.",
        "metadata": {
            "document_name": "UNICEF Annual Report 2025.pdf",
            "page": 18,
            "chunk_id": "chunk_0050"
        }
    }
]

answer = generate_answer(question, retrieved_documents)

print("\n--- Gemini Answer ---")
print(answer)