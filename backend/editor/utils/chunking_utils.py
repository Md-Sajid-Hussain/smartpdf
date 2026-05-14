import re


MAX_WORDS_PER_CHUNK = 700


def split_text_into_chunks(text, max_words=MAX_WORDS_PER_CHUNK):
    """
    Split large text into smaller chunks.

    Returns:
        List[str]
    """

    if not text:
        return []

    # Clean excessive spaces
    text = re.sub(r"\s+", " ", text).strip()

    words = text.split()

    chunks = []

    current_chunk = []

    current_length = 0

    for word in words:

        current_chunk.append(word)

        current_length += 1

        # Reached chunk size
        if current_length >= max_words:

            chunks.append(" ".join(current_chunk))

            current_chunk = []

            current_length = 0

    # Remaining words
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def split_text_by_paragraphs(text, max_words=MAX_WORDS_PER_CHUNK):
    """
    Better semantic chunking using paragraphs.

    Keeps context more naturally than fixed word split.
    """

    if not text:
        return []

    paragraphs = text.split("\n")

    chunks = []

    current_chunk = ""

    current_word_count = 0

    for para in paragraphs:

        para = para.strip()

        if not para:
            continue

        para_word_count = len(para.split())

        # If adding paragraph exceeds limit
        if current_word_count + para_word_count > max_words:

            if current_chunk:
                chunks.append(current_chunk.strip())

            current_chunk = para
            current_word_count = para_word_count

        else:

            current_chunk += "\n" + para
            current_word_count += para_word_count

    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks