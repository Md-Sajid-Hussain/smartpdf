import os
import uuid
import traceback
import fitz
import ocrmypdf


from django.conf import settings
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from editor.services.ocr_service import perform_ocr
from editor.utils.extraction_utils import extract_text_from_pdf
from editor.services.summary_service import generate_summary
from editor.services.question_service import generate_questions
from editor.services.notes_service import generate_notes




def _save_uploaded_pdf(uploaded_file):
    """
    Save uploaded PDF temporarily and return absolute file path.
    """
    temp_filename = f"temp_{uuid.uuid4().hex}.pdf"
    saved_name = default_storage.save(temp_filename, ContentFile(uploaded_file.read()))
    return default_storage.path(saved_name)


def _safe_remove(path):
    """
    Remove file if it exists. Fail silently.
    """
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def _normalize_extraction_result(result):
    """
    Make extraction result safe even if an old function returns a string.
    Expected format from utils/extraction_utils.py:
        {"success": True/False, "text": "...", "error": "..."}
    """
    if isinstance(result, dict):
        return result

    if isinstance(result, str):
        text = result.strip()
        if not text:
            return {
                "success": False,
                "error": "No readable text found in PDF"
            }
        return {
            "success": True,
            "text": text
        }

    return {
        "success": False,
        "error": f"Unexpected extraction result type: {type(result).__name__}"
    }


@csrf_exempt
@require_http_methods(["POST"])
def ocr_pdf_api(request):
    """
    Real OCR endpoint using OCRmyPDF.
    Returns selectable PDF for download.
    """
    try:
        file = request.FILES.get("file")

        if not file:
            return JsonResponse({"error": "No PDF file provided"}, status=400)

        if not file.name.lower().endswith(".pdf"):
            return JsonResponse({"error": "Only PDF files are allowed"}, status=400)

        input_pdf_path = _save_uploaded_pdf(file)

        # Perform OCR
        result = perform_ocr(input_pdf_path)

        # Remove uploaded temp file
        _safe_remove(input_pdf_path)

        if not result["success"]:
            return JsonResponse({"error": result["error"]}, status=500)

        output_pdf_path = result["output_path"]

        if not os.path.exists(output_pdf_path):
            return JsonResponse({"error": "OCR output file not generated"}, status=500)


        # ==========================================
        # RETURN JSON RESPONSE
        # ==========================================

        filename = os.path.basename(output_pdf_path)

        print("JSON RESPONSE IS RUNNING")

        doc = fitz.open(output_pdf_path)

        extracted_text = ""

        for page in doc:
            extracted_text += page.get_text()

        return JsonResponse({
            "success": True,
            "message": "OCR completed successfully",
            "download_url": f"/media/output/{filename}",
            "filename": filename,
            "extracted_text": extracted_text
        })



    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def summarize_pdf_api(request):
    """
    Real AI PDF summarization endpoint.
    """
    try:
        file = request.FILES.get("file")

        if not file:
            return JsonResponse({"error": "No PDF file provided"}, status=400)

        if not file.name.lower().endswith(".pdf"):
            return JsonResponse({"error": "Only PDF files are allowed"}, status=400)

        pdf_path = _save_uploaded_pdf(file)

        extraction_result = _normalize_extraction_result(
            extract_text_from_pdf(pdf_path)
        )

        _safe_remove(pdf_path)

        if not extraction_result["success"]:
            return JsonResponse({"error": extraction_result["error"]}, status=400)

        extracted_text = extraction_result["text"]

        summary_result = generate_summary(extracted_text)

        if not summary_result["success"]:
            return JsonResponse({"error": summary_result["error"]}, status=500)

        return JsonResponse({
            "result": summary_result["summary"],
            "word_count": summary_result["word_count"],
            "chunks_processed": summary_result["total_chunks"],
            "type": "summary"
        })

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_questions_api(request):
    """
    Real AI question generation endpoint.
    """
    try:
        file = request.FILES.get("file")

        if not file:
            return JsonResponse({"error": "No PDF file provided"}, status=400)

        if not file.name.lower().endswith(".pdf"):
            return JsonResponse({"error": "Only PDF files are allowed"}, status=400)

        pdf_path = _save_uploaded_pdf(file)

        extraction_result = _normalize_extraction_result(
            extract_text_from_pdf(pdf_path)
        )

        _safe_remove(pdf_path)

        if not extraction_result["success"]:
            return JsonResponse({"error": extraction_result["error"]}, status=400)

        extracted_text = extraction_result["text"]

        question_result = generate_questions(extracted_text)

        if not question_result["success"]:
            return JsonResponse({"error": question_result["error"]}, status=500)

        return JsonResponse({
            "result": "\n\n".join(
                [f"{idx + 1}. {q}" for idx, q in enumerate(question_result["questions"])]
            ),
            "questions": question_result["questions"],
            "total_questions": question_result["total_questions"],
            "chunks_processed": question_result["chunks_processed"],
            "type": "questions"
        })

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def make_notes_api(request):
    """
    Real AI notes generation endpoint.
    """
    try:
        file = request.FILES.get("file")

        if not file:
            return JsonResponse({"error": "No PDF file provided"}, status=400)

        if not file.name.lower().endswith(".pdf"):
            return JsonResponse({"error": "Only PDF files are allowed"}, status=400)

        pdf_path = _save_uploaded_pdf(file)

        extraction_result = _normalize_extraction_result(
            extract_text_from_pdf(pdf_path)
        )

        _safe_remove(pdf_path)

        if not extraction_result["success"]:
            return JsonResponse({"error": extraction_result["error"]}, status=400)

        extracted_text = extraction_result["text"]

        notes_result = generate_notes(extracted_text)

        if not notes_result["success"]:
            return JsonResponse({"error": notes_result["error"]}, status=500)

        return JsonResponse({
            "result": notes_result["notes"],
            "keywords_found": notes_result["keywords_found"],
            "chunks_processed": notes_result["total_chunks"],
            "type": "notes"
        })

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)