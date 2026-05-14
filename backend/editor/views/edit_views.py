# from django.http import HttpResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
# import json
# import os
# import uuid
# from ..utils.edit_utils import replace_text_multiple, insert_image, get_pdf_info

# MEDIA_PATH = "media"

# @csrf_exempt
# @require_http_methods(["POST"])
# def replace_text_api(request):
#     """
#     API endpoint to replace/add text to PDF
#     Expects: file (PDF), text_elements (JSON string)
#     """
#     try:
#         # Get uploaded file
#         pdf_file = request.FILES.get('file')
#         if not pdf_file:
#             return JsonResponse({'error': 'No file provided'}, status=400)
        
#         # Get text elements
#         text_elements_str = request.POST.get('text_elements')
#         if not text_elements_str:
#             return JsonResponse({'error': 'No text elements provided'}, status=400)
        
#         text_elements = json.loads(text_elements_str)
        
#         # Save uploaded file temporarily
#         os.makedirs(MEDIA_PATH, exist_ok=True)
#         temp_input_path = os.path.join(MEDIA_PATH, f"input_{uuid.uuid4()}.pdf")
        
#         with open(temp_input_path, 'wb') as f:
#             for chunk in pdf_file.chunks():
#                 f.write(chunk)
        
#         # Process all text elements (assuming all on page 0 for now)
#         # Get page number from first element or default to 0
#         page_number = text_elements[0].get('page', 0) if text_elements else 0
        
#         # Call utility to add all texts
#         output_path = replace_text_multiple(
#             temp_input_path, 
#             text_elements, 
#             page_number=page_number
#         )
        
#         # Clean up input file
#         if os.path.exists(temp_input_path):
#             os.remove(temp_input_path)
        
#         # Return the modified PDF
#         with open(output_path, 'rb') as f:
#             response = HttpResponse(f.read(), content_type='application/pdf')
#             response['Content-Disposition'] = 'attachment; filename="edited.pdf"'
        
#         # Clean up output file after sending
#         if os.path.exists(output_path):
#             os.remove(output_path)
        
#         return response
        
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


# @csrf_exempt
# @require_http_methods(["POST"])
# def insert_image_api(request):
#     """
#     API endpoint to insert image into PDF
#     Expects: file (PDF), image (file), page, x, y
#     """
#     try:
#         # Get uploaded PDF
#         pdf_file = request.FILES.get('file')
#         if not pdf_file:
#             return JsonResponse({'error': 'No PDF file provided'}, status=400)
        
#         # Get uploaded image
#         image_file = request.FILES.get('image')
#         if not image_file:
#             return JsonResponse({'error': 'No image file provided'}, status=400)
        
#         # Get parameters
#         page_number = int(request.POST.get('page', 0))
#         x = float(request.POST.get('x', 100))
#         y = float(request.POST.get('y', 100))
#         width = float(request.POST.get('width', 150))
#         height = float(request.POST.get('height', 150))
        
#         # Save uploaded files temporarily
#         os.makedirs(MEDIA_PATH, exist_ok=True)
#         temp_pdf_path = os.path.join(MEDIA_PATH, f"input_{uuid.uuid4()}.pdf")
#         temp_image_path = os.path.join(MEDIA_PATH, f"image_{uuid.uuid4()}.png")
        
#         with open(temp_pdf_path, 'wb') as f:
#             for chunk in pdf_file.chunks():
#                 f.write(chunk)
        
#         with open(temp_image_path, 'wb') as f:
#             for chunk in image_file.chunks():
#                 f.write(chunk)
        
#         # Insert image
#         output_path = insert_image(
#             temp_pdf_path, 
#             temp_image_path, 
#             x, y, 
#             width=width, 
#             height=height, 
#             page_number=page_number
#         )
        
#         # Clean up temp files
#         if os.path.exists(temp_pdf_path):
#             os.remove(temp_pdf_path)
#         if os.path.exists(temp_image_path):
#             os.remove(temp_image_path)
        
#         # Return modified PDF
#         with open(output_path, 'rb') as f:
#             response = HttpResponse(f.read(), content_type='application/pdf')
#             response['Content-Disposition'] = 'attachment; filename="edited_with_image.pdf"'
        
#         # Clean up output file
#         if os.path.exists(output_path):
#             os.remove(output_path)
        
#         return response
        
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


# @csrf_exempt
# @require_http_methods(["POST"])
# def delete_pages_api(request):
#     """
#     API endpoint to delete pages from PDF
#     Expects: file (PDF), pages (string like "1,2,4" or "1:5")
#     """
#     try:
#         import fitz
        
#         pdf_file = request.FILES.get('file')
#         if not pdf_file:
#             return JsonResponse({'error': 'No file provided'}, status=400)
        
#         pages_input = request.POST.get('pages', '')
#         if not pages_input:
#             return JsonResponse({'error': 'No pages specified'}, status=400)
        
#         # Parse pages input
#         pages_to_delete = set()
        
#         if ':' in pages_input:
#             # Range like "1:5"
#             start, end = map(int, pages_input.split(':'))
#             pages_to_delete = set(range(start - 1, end))  # Convert to 0-index
#         elif ',' in pages_input:
#             # List like "1,2,4"
#             pages_to_delete = {int(p.strip()) - 1 for p in pages_input.split(',')}
#         else:
#             # Single page
#             pages_to_delete = {int(pages_input) - 1}
        
#         # Save uploaded file
#         os.makedirs(MEDIA_PATH, exist_ok=True)
#         temp_input_path = os.path.join(MEDIA_PATH, f"input_{uuid.uuid4()}.pdf")
        
#         with open(temp_input_path, 'wb') as f:
#             for chunk in pdf_file.chunks():
#                 f.write(chunk)
        
#         # Open PDF and delete pages
#         doc = fitz.open(temp_input_path)
        
#         # Delete pages in reverse order to maintain indices
#         for page_num in sorted(pages_to_delete, reverse=True):
#             if 0 <= page_num < len(doc):
#                 doc.delete_page(page_num)
        
#         # Save modified PDF
#         output_path = os.path.join(MEDIA_PATH, f"output_{uuid.uuid4()}.pdf")
#         doc.save(output_path)
#         doc.close()
        
#         # Clean up input file
#         if os.path.exists(temp_input_path):
#             os.remove(temp_input_path)
        
#         # Return modified PDF
#         with open(output_path, 'rb') as f:
#             response = HttpResponse(f.read(), content_type='application/pdf')
#             response['Content-Disposition'] = 'attachment; filename="pages_deleted.pdf"'
        
#         # Clean up output file
#         if os.path.exists(output_path):
#             os.remove(output_path)
        
#         return response
        
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


# @csrf_exempt
# @require_http_methods(["GET"])
# def pdf_preview_api(request, page_num=1):
#     """
#     API endpoint to get PDF page preview as image
#     """
#     try:
#         # This requires the PDF file to be passed as a query parameter or session
#         # For now, returns a placeholder
#         return JsonResponse({'message': 'Preview endpoint - implement with file storage'}, status=200)
        
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)







from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import uuid
from ..utils.edit_utils import replace_text_multiple, insert_image, get_pdf_info

MEDIA_PATH = "media"

@csrf_exempt
@require_http_methods(["POST"])
def replace_text_api(request):
    """
    API endpoint to replace/add text to PDF
    Expects: file (PDF), text_elements (JSON string)
    """
    try:
        # Get uploaded file
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        # Get text elements
        text_elements_str = request.POST.get('text_elements')
        if not text_elements_str:
            return JsonResponse({'error': 'No text elements provided'}, status=400)
        
        text_elements = json.loads(text_elements_str)
        
        # Save uploaded file temporarily
        os.makedirs(MEDIA_PATH, exist_ok=True)
        temp_input_path = os.path.join(MEDIA_PATH, f"input_{uuid.uuid4()}.pdf")
        
        with open(temp_input_path, 'wb') as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)
        
        # Process text elements on their respective pages
        # Group text elements by page
        text_by_page = {}
        for element in text_elements:
            page = element.get('page', 0)
            if page not in text_by_page:
                text_by_page[page] = []
            text_by_page[page].append(element)
        
        # Apply text changes page by page
        import fitz
        doc = fitz.open(temp_input_path)
        
        for page_num, elements in text_by_page.items():
            if 0 <= page_num < len(doc):
                page = doc[page_num]
                for element in elements:
                    # Add text at specified position
                    text = element.get('text', '')
                    x = element.get('x', 100)
                    y = element.get('y', 100)
                    font_size = element.get('fontSize', 16)
                    font_family = element.get('fontFamily', 'Arial')
                    font_color = element.get('fontColor', '#000000')
                    is_bold = element.get('isBold', False)
                    is_transparent = element.get('isTransparent', True)
                    
                    # Convert hex color to RGB
                    hex_color = font_color.lstrip('#')
                    rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    
                    # Set font weight
                    fontname = "helv"  # default
                    if is_bold:
                        fontname = "hebo"  # bold
                    
                    # Insert text
                    page.insert_text(
                        (x, y),
                        text,
                        fontsize=font_size,
                        fontname=fontname,
                        color=rgb_color,
                        render_mode=0 if not is_transparent else 1
                    )
        
        # Save modified PDF
        output_path = os.path.join(MEDIA_PATH, f"output_{uuid.uuid4()}.pdf")
        doc.save(output_path)
        doc.close()
        
        # Clean up input file
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        
        # Return the modified PDF
        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="edited.pdf"'
        
        # Clean up output file after sending
        if os.path.exists(output_path):
            os.remove(output_path)
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def insert_image_api(request):
    """
    API endpoint to insert image into PDF
    Expects: file (PDF), image (file), page, x, y
    """
    try:
        # Get uploaded PDF
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return JsonResponse({'error': 'No PDF file provided'}, status=400)
        
        # Get uploaded image
        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        # Get parameters
        page_number = int(request.POST.get('page', 0))
        x = float(request.POST.get('x', 100))
        y = float(request.POST.get('y', 100))
        width = float(request.POST.get('width', 150))
        height = float(request.POST.get('height', 150))
        
        # Save uploaded files temporarily
        os.makedirs(MEDIA_PATH, exist_ok=True)
        temp_pdf_path = os.path.join(MEDIA_PATH, f"input_{uuid.uuid4()}.pdf")
        temp_image_path = os.path.join(MEDIA_PATH, f"image_{uuid.uuid4()}.png")
        
        with open(temp_pdf_path, 'wb') as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)
        
        # Save image
        with open(temp_image_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        
        # Insert image using PyMuPDF
        import fitz
        doc = fitz.open(temp_pdf_path)
        
        if 0 <= page_number < len(doc):
            page = doc[page_number]
            # Insert image at specified position
            page.insert_image(
                fitz.Rect(x, y, x + width, y + height),
                filename=temp_image_path
            )
        
        # Save modified PDF
        output_path = os.path.join(MEDIA_PATH, f"output_{uuid.uuid4()}.pdf")
        doc.save(output_path)
        doc.close()
        
        # Clean up temp files
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        # Return modified PDF
        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="edited_with_image.pdf"'
        
        # Clean up output file
        if os.path.exists(output_path):
            os.remove(output_path)
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_pages_api(request):
    """
    API endpoint to delete pages from PDF
    Expects: file (PDF), pages (string like "1,2,4" or "1-5")
    """
    try:
        import fitz
        
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        pages_input = request.POST.get('pages', '')
        if not pages_input:
            return JsonResponse({'error': 'No pages specified'}, status=400)
        
        # Save uploaded file
        os.makedirs(MEDIA_PATH, exist_ok=True)
        temp_input_path = os.path.join(MEDIA_PATH, f"input_{uuid.uuid4()}.pdf")
        
        with open(temp_input_path, 'wb') as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)
        
        # Open PDF and get total pages
        doc = fitz.open(temp_input_path)
        total_pages = len(doc)
        
        # Parse pages input
        pages_to_delete = set()
        
        if '-' in pages_input:
            # Range like "1-5"
            parts = pages_input.split('-')
            if len(parts) == 2:
                start = int(parts[0])
                end = int(parts[1])
                if start < 1 or end > total_pages or start > end:
                    doc.close()
                    os.remove(temp_input_path)
                    return JsonResponse({'error': f'Invalid range. Page numbers should be between 1 and {total_pages}'}, status=400)
                pages_to_delete = set(range(start - 1, end))
        elif ',' in pages_input:
            # List like "1,2,4"
            for p in pages_input.split(','):
                page_num = int(p.strip())
                if page_num < 1 or page_num > total_pages:
                    doc.close()
                    os.remove(temp_input_path)
                    return JsonResponse({'error': f'Invalid page number {page_num}. Pages should be between 1 and {total_pages}'}, status=400)
                pages_to_delete.add(page_num - 1)
        else:
            # Single page
            page_num = int(pages_input)
            if page_num < 1 or page_num > total_pages:
                doc.close()
                os.remove(temp_input_path)
                return JsonResponse({'error': f'Invalid page number. Please enter a number between 1 and {total_pages}'}, status=400)
            pages_to_delete = {page_num - 1}
        
        # Delete pages in reverse order to maintain indices
        for page_num in sorted(pages_to_delete, reverse=True):
            if 0 <= page_num < len(doc):
                doc.delete_page(page_num)
        
        # Save modified PDF
        output_path = os.path.join(MEDIA_PATH, f"output_{uuid.uuid4()}.pdf")
        doc.save(output_path)
        doc.close()
        
        # Clean up input file
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        
        # Return modified PDF
        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="pages_deleted.pdf"'
        
        # Clean up output file
        if os.path.exists(output_path):
            os.remove(output_path)
        
        return response
        
    except ValueError:
        return JsonResponse({'error': 'Invalid input format. Please use formats like "5", "1,3,5", or "1-5"'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def insert_pdf_api(request):
    """
    API endpoint to insert one PDF into another
    Expects: file (PDF), insert_file (PDF), after_page (page number)
    """
    try:
        import fitz
        
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return JsonResponse({'error': 'No PDF file provided'}, status=400)
        
        insert_file = request.FILES.get('insert_file')
        if not insert_file:
            return JsonResponse({'error': 'No insert file provided'}, status=400)
        
        after_page = int(request.POST.get('after_page', 0))
        
        # Validate page number
        if after_page < 0:
            return JsonResponse({'error': 'Page number must be greater than or equal to 0'}, status=400)
        
        # Save uploaded files temporarily
        os.makedirs(MEDIA_PATH, exist_ok=True)
        temp_pdf_path = os.path.join(MEDIA_PATH, f"input_{uuid.uuid4()}.pdf")
        temp_insert_path = os.path.join(MEDIA_PATH, f"insert_{uuid.uuid4()}.pdf")
        
        with open(temp_pdf_path, 'wb') as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)
        
        with open(temp_insert_path, 'wb') as f:
            for chunk in insert_file.chunks():
                f.write(chunk)
        
        # Open both PDFs
        main_doc = fitz.open(temp_pdf_path)
        insert_doc = fitz.open(temp_insert_path)
        
        # Get total pages of main document
        total_pages = len(main_doc)
        
        # Validate after_page is within range
        if after_page > total_pages:
            main_doc.close()
            insert_doc.close()
            os.remove(temp_pdf_path)
            os.remove(temp_insert_path)
            return JsonResponse({'error': f'Invalid page number. Main PDF has {total_pages} pages. Please specify a page between 0 and {total_pages}'}, status=400)
        
        # Insert pages from insert_doc after the specified page
        # If after_page is 0, insert at beginning
        # If after_page equals total_pages, insert at end
        insert_position = after_page
        
        # Insert all pages from insert_doc
        for page_num in range(len(insert_doc)):
            main_doc.insert_pdf(insert_doc, from_page=page_num, to_page=page_num, start_at=insert_position + page_num)
        
        # Save modified PDF
        output_path = os.path.join(MEDIA_PATH, f"output_{uuid.uuid4()}.pdf")
        main_doc.save(output_path)
        
        # Close documents
        main_doc.close()
        insert_doc.close()
        
        # Clean up temp files
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        if os.path.exists(temp_insert_path):
            os.remove(temp_insert_path)
        
        # Return modified PDF
        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="pdf_inserted.pdf"'
        
        # Clean up output file
        if os.path.exists(output_path):
            os.remove(output_path)
        
        return response
        
    except ValueError as e:
        return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def pdf_preview_api(request, page_num=1):
    """
    API endpoint to get PDF page preview as image
    """
    try:
        # This requires the PDF file to be passed as a query parameter or session
        # For now, returns a placeholder
        return JsonResponse({'message': 'Preview endpoint - implement with file storage'}, status=200)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)