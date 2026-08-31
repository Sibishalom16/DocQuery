from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []

    for page in pages:
        page_text = page["text"]

        if not page_text.strip():
            continue

        page_chunks = splitter.split_text(page_text)

        for chunk in page_chunks:
            chunks.append({
                "page": page["page"],
                "text": chunk
            })

    return chunks