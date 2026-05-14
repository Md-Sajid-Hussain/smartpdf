import fitz
import os


def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using PyMuPDF.

    Returns:
        {
            "success": True/False,
            "text": "...",
            "pages": int,
            "error": "..."
        }
    """

    try:

        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "error": "PDF file does not exist"
            }

        doc = fitz.open(pdf_path)

        extracted_text = []

        total_pages = len(doc)

        for page in doc:

            page_text = page.get_text("text")

            if page_text:
                extracted_text.append(page_text)

        doc.close()

        final_text = "\n".join(extracted_text)

        final_text = clean_extracted_text(final_text)

        if not final_text.strip():
            return {
                "success": False,
                "error": "No readable text found in PDF"
            }

        return {
            "success": True,
            "text": final_text,
            "pages": total_pages
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


def clean_extracted_text(text):
    """
    Clean extracted PDF text.
    """

    if not text:
        return ""

    # Remove excessive blank lines
    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        cleaned_line = line.strip()

        if cleaned_line:
            cleaned_lines.append(cleaned_line)

    cleaned_text = "\n".join(cleaned_lines)

    # Remove excessive spaces
    cleaned_text = " ".join(cleaned_text.split())

    return cleaned_text