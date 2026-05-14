import re


def clean_generated_text(text):
    """
    Clean AI generated text.
    """

    if not text:
        return ""

    # Remove extra spaces
    text = text.strip()

    # Remove repeated spaces
    text = re.sub(r"\s+", " ", text)

    # Remove strange tokens
    text = text.replace("<pad>", "")
    text = text.replace("</s>", "")

    # Remove duplicate punctuation
    text = re.sub(r"\?{2,}", "?", text)
    text = re.sub(r"\.{2,}", ".", text)

    return text.strip()