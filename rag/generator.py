import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.6-flash"


def generate_answer(question, retrieved_documents):

    context_parts = []

    for document in retrieved_documents:
        metadata = document["metadata"]

        context_parts.append(
            f"""
Document: {metadata.get('document_name')}
Page: {metadata.get('page')}

Content:
{document['text']}
"""
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the retrieved document context.

Rules:
- Do not use outside knowledge.
- Do not invent information.
- If the context does not contain enough information to answer the question, say:
  "I couldn't find this information in the uploaded documents."
- Give a concise and clear answer.

Retrieved Context:
{context}

User Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text