from rag.pdf_loader import extract_text_from_pdf
from rag.text_cleaner import clean_text


def test_remove_extra_whitespace():
    text = "Hello    world.\n\n\nThis is a test."
    cleaned = clean_text(text)

    assert cleaned == "Hello world.\nThis is a test."


def test_fix_letter_spacing():
    text = "C ONSOLIDATED F INANCIAL S TATEMENTS"
    cleaned = clean_text(text)

    assert cleaned == "CONSOLIDATED FINANCIAL STATEMENTS"


def test_fix_broken_word():
    text = "DEV ELOPMENT"
    cleaned = clean_text(text)

    assert cleaned == "DEVELOPMENT"


def test_preserve_paragraphs():
    text = "Article I\nStandard Conditions\n\n1.01. The conditions apply."
    cleaned = clean_text(text)

    assert "Article I\nStandard Conditions" in cleaned
    assert "1.01. The conditions apply." in cleaned


def test_real_pdf():
    pdf_path = "data/uploads/UNICEF Annual Report 2025.pdf"

    pages = extract_text_from_pdf(pdf_path)

    for page in pages[:3]:
        cleaned = clean_text(page["text"])

        print(f"\n--- Page {page['page']} ---")
        print("BEFORE:")
        print(repr(page["text"][:300]))

        print("AFTER:")
        print(repr(cleaned[:300]))