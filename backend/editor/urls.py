from django.urls import path
from .views.ocr_views import ocr_pdf_api
from .views.edit_views import replace_text_api, insert_image_api, insert_pdf_api
from .views.convert_views import (
    pdf_to_word_api,
    word_to_pdf_api,
    pdf_to_image_api,
    image_to_pdf_api,
    ppt_to_pdf_api,
    excel_to_pdf_api
)
# Import new views
from .views.pdf_operations_views import (
    merge_pdfs_api,
    split_pdf_api,
    delete_pages_api,
    extract_pages_api,
    view_pdf_api,
    pdf_preview_api
)
from .views.ai_views import (
    ocr_pdf_api,
    summarize_pdf_api,
    generate_questions_api,
    make_notes_api
)

# NEW IMPORT for split chatbot functionality
from .views.split_views import (
    upload_pdf_api,
    split_command_api,
    download_pdf_api,
    download_zip_api,
    cleanup_session_api
)

urlpatterns = [
    # EDIT
    path('replace-text/', replace_text_api),
    path('insert-image/', insert_image_api),
    path('insert-pdf/', insert_pdf_api, name='insert_pdf'),

    # CONVERT
    path('pdf-to-word/', pdf_to_word_api), # ✅
    path('word-to-pdf/', word_to_pdf_api), # ✅
    path('pdf-to-image/', pdf_to_image_api), # ✅
    path('image-to-pdf/', image_to_pdf_api), # ✅
    path('ppt-to-pdf/', ppt_to_pdf_api), # ✅
    path('excel-to-pdf/', excel_to_pdf_api), # ✅
    
    # NEW PDF OPERATIONS
    path('merge-pdf/', merge_pdfs_api),    # ✅                # POST: merge multiple PDFs
    path('split/', split_pdf_api),                     # POST: split PDF into pages
    path('delete-pages/', delete_pages_api),           # POST: delete specific pages
    path('extract-pages/', extract_pages_api),         # POST: extract pages to new PDF
    path('view/', view_pdf_api),                       # GET: get PDF metadata & text
    path('preview/<int:page_num>/', pdf_preview_api),  # GET: get image preview of a page

    # AI & ADVANCED OPERATIONS
    path('ocr/', ocr_pdf_api),
    path('summarize/', summarize_pdf_api),
    path('generate-questions/', generate_questions_api),
    path('make-notes/', make_notes_api),
    
    # NEW SPLIT CHATBOT ENDPOINTS (add these)
    path('split/upload/', upload_pdf_api, name='split_upload'),
    path('split/command/', split_command_api, name='split_command'),
    path('split/download/<str:session_id>/pdf/', download_pdf_api, name='split_download_pdf'),
    path('split/download/<str:session_id>/zip/', download_zip_api, name='split_download_zip'),
    path('split/cleanup/<str:session_id>/', cleanup_session_api, name='split_cleanup'),
]