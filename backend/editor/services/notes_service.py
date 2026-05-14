from yake import KeywordExtractor

from editor.services.summary_service import (
    generate_summary
)

from editor.utils.chunking_utils import (
    split_text_into_chunks
)

# =========================================================
# YAKE KEYWORD EXTRACTOR
# =========================================================

keyword_extractor = KeywordExtractor(
    lan="en",
    n=2,
    dedupLim=0.7,
    top=12
)


# =========================================================
# GENERATE NOTES
# =========================================================

def generate_notes(extracted_text):
    """
    Generate structured study notes.
    """

    try:

        if not extracted_text.strip():

            return {
                "success": False,
                "error": "No text available for notes generation"
            }

        # Generate summary first
        summary_result = generate_summary(
            extracted_text
        )

        if not summary_result["success"]:

            return {
                "success": False,
                "error": summary_result["error"]
            }

        summary_text = summary_result["summary"]

        # Extract keywords
        keywords = keyword_extractor.extract_keywords(
            extracted_text[:5000]
        )

        keyword_list = []

        for kw, score in keywords:

            if len(kw.split()) <= 4:
                keyword_list.append(kw)

        # Create notes
        notes_lines = []

        notes_lines.append(
            "## SMART STUDY NOTES\n"
        )

        notes_lines.append(
            "### SUMMARY\n"
        )

        notes_lines.append(summary_text)

        notes_lines.append("\n")

        notes_lines.append(
            "### IMPORTANT TOPICS\n"
        )

        for keyword in keyword_list:

            notes_lines.append(
                f"• {keyword}"
            )

        notes_lines.append("\n")

        # Additional chunk summaries
        chunks = split_text_into_chunks(
            extracted_text,
            max_words=400
        )

        notes_lines.append(
            "### SECTION INSIGHTS\n"
        )

        for idx, chunk in enumerate(chunks[:5]):

            chunk_summary_result = generate_summary(
                chunk
            )

            if chunk_summary_result["success"]:

                notes_lines.append(
                    f"\nSECTION {idx + 1}"
                )

                notes_lines.append(
                    chunk_summary_result["summary"]
                )

        final_notes = "\n".join(notes_lines)

        return {
            "success": True,
            "notes": final_notes,
            "keywords_found": len(keyword_list),
            "total_chunks": len(chunks)
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }