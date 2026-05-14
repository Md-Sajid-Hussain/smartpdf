from transformers import pipeline

from editor.utils.chunking_utils import (
    split_text_into_chunks
)

# =========================================================
# LOAD SUMMARIZATION MODEL
# =========================================================

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=-1
)


# =========================================================
# GENERATE SUMMARY
# =========================================================

def generate_summary(extracted_text):
    """
    Generate AI summary from extracted PDF text.
    """

    try:

        if not extracted_text.strip():

            return {
                "success": False,
                "error": "No text available for summarization"
            }

        # Split text into chunks
        chunks = split_text_into_chunks(
            extracted_text,
            max_words=400
        )

        summaries = []

        for chunk in chunks:

            chunk = chunk.strip()

            if len(chunk.split()) < 30:
                continue

            # Dynamic summary lengths
            word_count = len(chunk.split())

            max_len = min(
                120,
                max(40, word_count // 2)
            )

            min_len = min(
                60,
                max(15, word_count // 4)
            )

            # Generate summary
            result = summarizer(
                chunk,
                max_length=max_len,
                min_length=min_len,
                do_sample=False
            )

            chunk_summary = (
                result[0]["summary_text"]
            )

            summaries.append(
                chunk_summary
            )

        if not summaries:

            return {
                "success": False,
                "error": "Could not generate summary"
            }

        final_summary = "\n\n".join(
            summaries
        )

        return {
            "success": True,
            "summary": final_summary,
            "word_count": len(
                extracted_text.split()
            ),
            "total_chunks": len(chunks)
        }

    except Exception as e:

        import traceback

        traceback.print_exc()

        return {
            "success": False,
            "error": str(e)
        }