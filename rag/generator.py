import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-20b"


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
- Mention relevant details from the retrieved context.
- Do not answer using information from documents that are not included in the retrieved context.

Retrieved Context:
{context}

User Question:
{question}

Answer:
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a document question-answering assistant. "
                        "Answer questions only using the provided retrieved "
                        "document context. Never invent information."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        answer_text = response.choices[0].message.content
        if not answer_text or str(answer_text).strip() == "":
            return "Unable to generate an answer. The model returned an empty response."
        return answer_text

    except Exception as e:
        error_msg = str(e).lower()

        if (
            "429" in error_msg
            or "resource_exhausted" in error_msg
            or "503" in error_msg
            or "unavailable" in error_msg
            or "quota" in error_msg
        ):
            return "AI service is temporarily unavailable. Please try again later."

        return "Unable to generate an answer right now. Please try again."