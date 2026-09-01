from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text):
    """Generate an embedding for a single text."""
    return model.encode(text).tolist()


def generate_embeddings(texts):
    """Generate embeddings for multiple texts."""
    return model.encode(texts).tolist()