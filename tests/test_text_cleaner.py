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
