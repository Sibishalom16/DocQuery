import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBEDDING_MODEL = "gemini-embedding-001"


def generate_embedding(text):
    """Generate a Gemini embedding for a single text."""
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )

    return response.embeddings[0].values


def generate_embeddings(texts):
    """Generate Gemini embeddings for multiple texts."""
    return [generate_embedding(text) for text in texts]