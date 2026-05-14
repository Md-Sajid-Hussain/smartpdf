import os
import uuid
import traceback
import ocrmypdf

# ==========================================
# BASE PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

MEDIA_DIR = os.path.join(BASE_DIR, "media")

OUTPUT_DIR = os.path.join(
    MEDIA_DIR,
    "output"
)

# Create folders automatically
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================
# OCR FUNCTION
# ==========================================

def perform_ocr(input_pdf_path):

    try:

        # Unique output filename
        filename = f"temp_{uuid.uuid4().hex}_ocr.pdf"

        # Final output path
        output_pdf_path = os.path.join(
            OUTPUT_DIR,
            filename
        )

        print("\n========== OCR DEBUG ==========")
        print("INPUT:", input_pdf_path)
        print("OUTPUT:", output_pdf_path)
        print("================================\n")

        # OCR PROCESS
        ocrmypdf.ocr(
            input_pdf_path,
            output_pdf_path,
            force_ocr=True,
            language="eng+hin",
            deskew=True
        )

        # Verify file created
        if not os.path.exists(output_pdf_path):

            return {
                "success": False,
                "error": "OCR output file was not created"
            }

        return {
            "success": True,
            "output_path": output_pdf_path
        }

    except Exception as e:

        traceback.print_exc()

        return {
            "success": False,
            "error": str(e)
        }