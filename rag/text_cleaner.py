import re


def clean_text(text):
    # Normalize spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove unnecessary blank lines
    text = re.sub(r"\n\s*\n+", "\n", text)

    # Fix simple PDF letter spacing
    text = re.sub(r"\b([A-Z]) ([A-Z]{2,})\b", r"\1\2", text)

    # Fix known broken words
    broken_words = {
        "DEV ELOPMENT": "DEVELOPMENT",
    }

    for broken, corrected in broken_words.items():
        text = text.replace(broken, corrected)

    return text.strip()