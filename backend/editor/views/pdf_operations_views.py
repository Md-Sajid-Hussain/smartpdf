import os
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import fitz
from PIL import Image
import uuid
import zipfile
import spacy
import re
from datetime import datetime
from collections import defaultdict

MEDIA_PATH = "media"

@csrf_exempt
@require_http_methods(["POST"])
def merge_pdfs_api(request):
    """Merge multiple PDF files"""
    try:
        pdf_files = request.FILES.getlist('pdfs')  # Get all uploaded PDFs
        
        if len(pdf_files) < 2:
            return JsonResponse({"error": "At least 2 PDF files required"}, status=400)
        
        # Save uploaded files temporarily
        temp_paths = []
        for pdf in pdf_files:
            temp_path = default_storage.save(f"temp_{uuid.uuid4()}.pdf", ContentFile(pdf.read()))
            temp_paths.append(default_storage.path(temp_path))
        
        # Merge PDFs
        result = fitz.open()
        for path in temp_paths:
            doc = fitz.open(path)
            result.insert_pdf(doc)
            doc.close()
        
        # Save merged PDF
        output_filename = f"merged_{uuid.uuid4()}.pdf"
        output_path = os.path.join(MEDIA_PATH, output_filename)
        os.makedirs(MEDIA_PATH, exist_ok=True)
        result.save(output_path)
        result.close()
        
        # Clean up temp files
        for path in temp_paths:
            os.remove(path)
        
        # Return the file
        return FileResponse(open(output_path, 'rb'), 
                          content_type='application/pdf',
                          headers={'Content-Disposition': f'attachment; filename="{output_filename}"'})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def split_pdf_api(request):
    """Split PDF into individual pages"""
    try:
        pdf_file = request.FILES.get('pdf')
        if not pdf_file:
            return JsonResponse({"error": "PDF file required"}, status=400)
        
        # Save temp file
        temp_path = default_storage.save(f"temp_{uuid.uuid4()}.pdf", ContentFile(pdf_file.read()))
        temp_full_path = default_storage.path(temp_path)
        
        # Split PDF
        doc = fitz.open(temp_full_path)
        output_files = []
        
        for page_num in range(len(doc)):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            output_filename = f"page_{page_num+1}_{uuid.uuid4()}.pdf"
            output_path = os.path.join(MEDIA_PATH, output_filename)
            new_doc.save(output_path)
            new_doc.close()
            output_files.append(output_path)
        
        doc.close()
        os.remove(temp_full_path)
        
        # Create ZIP archive
        zip_filename = f"split_{uuid.uuid4()}.zip"
        zip_path = os.path.join(MEDIA_PATH, zip_filename)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i, file_path in enumerate(output_files):
                zipf.write(file_path, arcname=f"page_{i+1}.pdf")
                os.remove(file_path) # Clean up individual PDF files
        
        return FileResponse(open(zip_path, 'rb'), 
                            content_type='application/zip',
                            headers={'Content-Disposition': f'attachment; filename="split_pages.zip"'})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def delete_pages_api(request):
    """Delete specific pages from PDF"""
    try:
        pdf_file = request.FILES.get('pdf')
        pages_to_delete = json.loads(request.POST.get('pages', '[]'))  # e.g., [1, 3, 5]
        
        if not pdf_file:
            return JsonResponse({"error": "PDF file required"}, status=400)
        if not pages_to_delete:
            return JsonResponse({"error": "Pages to delete required"}, status=400)
        
        # Save temp file
        temp_path = default_storage.save(f"temp_{uuid.uuid4()}.pdf", ContentFile(pdf_file.read()))
        temp_full_path = default_storage.path(temp_path)
        
        # Delete pages
        doc = fitz.open(temp_full_path)
        # Delete in reverse order
        for page_num in sorted(pages_to_delete, reverse=True):
            if 1 <= page_num <= len(doc):
                doc.delete_page(page_num - 1)
        
        output_filename = f"modified_{uuid.uuid4()}.pdf"
        output_path = os.path.join(MEDIA_PATH, output_filename)
        doc.save(output_path)
        doc.close()
        os.remove(temp_full_path)
        
        return FileResponse(open(output_path, 'rb'),
                          content_type='application/pdf',
                          headers={'Content-Disposition': f'attachment; filename="{output_filename}"'})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def extract_pages_api(request):
    """Extract specific pages to new PDF"""
    try:
        pdf_file = request.FILES.get('pdf')
        pages_to_extract = json.loads(request.POST.get('pages', '[]'))  # e.g., [1, 3, 5]
        
        if not pdf_file:
            return JsonResponse({"error": "PDF file required"}, status=400)
        if not pages_to_extract:
            return JsonResponse({"error": "Pages to extract required"}, status=400)
        
        # Save temp file
        temp_path = default_storage.save(f"temp_{uuid.uuid4()}.pdf", ContentFile(pdf_file.read()))
        temp_full_path = default_storage.path(temp_path)
        
        # Extract pages
        doc = fitz.open(temp_full_path)
        new_doc = fitz.open()
        
        for page_num in pages_to_extract:
            if 1 <= page_num <= len(doc):
                new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
        
        output_filename = f"extracted_{uuid.uuid4()}.pdf"
        output_path = os.path.join(MEDIA_PATH, output_filename)
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        os.remove(temp_full_path)
        
        return FileResponse(open(output_path, 'rb'),
                          content_type='application/pdf',
                          headers={'Content-Disposition': f'attachment; filename="{output_filename}"'})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def view_pdf_api(request):
    """Get PDF metadata and text content (not visual preview)"""
    try:
        pdf_path = request.GET.get('path')
        if not pdf_path:
            return JsonResponse({"error": "PDF path required"}, status=400)
        
        if not os.path.exists(pdf_path):
            return JsonResponse({"error": "PDF file not found"}, status=404)
        
        doc = fitz.open(pdf_path)
        result = {
            "total_pages": len(doc),
            "metadata": doc.metadata,
            "text_content": []
        }
        
        # Get text from first 10 pages only (to avoid large responses)
        for page_num in range(min(10, len(doc))):
            page = doc[page_num]
            result["text_content"].append({
                "page": page_num + 1,
                "text": page.get_text()[:1000]  # Limit text per page
            })
        
        doc.close()
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def pdf_preview_api(request, page_num=1):
    """Get image preview of a specific PDF page"""
    try:
        pdf_path = request.GET.get('path')
        if not pdf_path:
            return JsonResponse({"error": "PDF path required"}, status=400)
        
        if not os.path.exists(pdf_path):
            return JsonResponse({"error": "PDF file not found"}, status=404)
        
        # Get zoom/preview size
        zoom = float(request.GET.get('zoom', 1.5))
        
        doc = fitz.open(pdf_path)
        if page_num < 1 or page_num > len(doc):
            doc.close()
            return JsonResponse({"error": f"Page {page_num} not found. Total pages: {len(doc)}"}, status=400)
        
        page = doc[page_num - 1]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PNG bytes
        img_data = pix.tobytes("png")
        doc.close()
        
        # Return as image response
        return HttpResponse(img_data, content_type="image/png")
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)