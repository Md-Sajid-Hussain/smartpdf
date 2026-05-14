import os
import uuid
import fitz
import ocrmypdf

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def ocr_pdf_api(request):

    try:

        # ============================================
        # CHECK REQUEST METHOD
        # ============================================

        if request.method != "POST":

            return JsonResponse({
                "success": False,
                "error": "Only POST method allowed"
            })

        # ============================================
        # CHECK FILE
        # ============================================

        uploaded_file = request.FILES.get("file")

        if not uploaded_file:

            return JsonResponse({
                "success": False,
                "error": "No PDF file uploaded"
            })

        # ============================================
        # CREATE INPUT FOLDER
        # ============================================

        input_folder = os.path.join(
            settings.MEDIA_ROOT,
            "input"
        )

        os.makedirs(
            input_folder,
            exist_ok=True
        )

        # ============================================
        # SAVE INPUT PDF
        # ============================================

        input_filename = (
            f"{uuid.uuid4().hex}.pdf"
        )

        input_pdf_path = os.path.join(
            input_folder,
            input_filename
        )

        with open(
            input_pdf_path,
            "wb+"
        ) as destination:

            for chunk in uploaded_file.chunks():

                destination.write(chunk)

        # ============================================
        # CREATE OUTPUT FOLDER
        # ============================================

        output_folder = os.path.join(
            settings.MEDIA_ROOT,
            "output"
        )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        # ============================================
        # OUTPUT FILE NAME
        # ============================================

        output_filename = (
            f"{uuid.uuid4().hex}_ocr.pdf"
        )

        output_pdf_path = os.path.join(
            output_folder,
            output_filename
        )

        # ============================================
        # RUN OCR
        # ============================================

        ocrmypdf.ocr(
            input_pdf_path,
            output_pdf_path,
            force_ocr=True,
            language="eng+hin"
        )

        # ============================================
        # EXTRACT TEXT
        # ============================================

        doc = fitz.open(
            output_pdf_path
        )

        extracted_text = ""

        for page in doc:

            extracted_text += (
                page.get_text()
            )

        doc.close()

        # ============================================
        # RETURN JSON RESPONSE
        # ============================================

        return JsonResponse({

            "success": True,

            "message": "OCR completed successfully",

            "download_url":
                f"/media/output/{output_filename}",

            "filename":
                output_filename,

            "extracted_text":
                extracted_text
        })

    except Exception as e:

        return JsonResponse({

            "success": False,

            "error": str(e)

        })