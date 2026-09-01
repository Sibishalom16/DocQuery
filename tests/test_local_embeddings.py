from rag.embeddings import generate_embeddings


texts = [
    "UNICEF works to protect children's rights.",
    "Children need access to education and healthcare.",
    "Financial reports contain revenue and expenses."
]

embeddings = generate_embeddings(texts)

print("Texts:", len(texts))
print("Embeddings:", len(embeddings))
print("Embedding dimensions:", len(embeddings[0]))

assert len(embeddings) == 3
assert len(embeddings[0]) > 0

print("Local embedding test passed!")