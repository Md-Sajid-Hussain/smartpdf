import os
import uuid
import fitz  # PyMuPDF for PDF operations
from PIL import Image
from pdf2docx import Converter  # Keep this for PDF→Word
from docx2pdf import convert     # Keep this for Word→PDF
try:
    import win32com.client
except ImportError:
    win32com = None
import pythoncom

MEDIA_PATH = "media"
os.makedirs(MEDIA_PATH, exist_ok=True)

# ========== YOUR ORIGINAL WORD FUNCTIONS (KEEP AS IS) ==========
def pdf_to_word(file_path):
    output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}.docx")
    cv = Converter(file_path)
    cv.convert(output)
    cv.close()
    return output

def word_to_pdf(file_path):
    pythoncom.CoInitialize()
    try:
        output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}.pdf")
        convert(file_path, output)
        return output
    finally:
        pythoncom.CoUninitialize()

def ppt_to_pdf(file_path):
    pythoncom.CoInitialize()
    try:
        powerpoint = win32com.client.Dispatch("Powerpoint.Application")
        output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}.pdf")
        abs_in = os.path.abspath(file_path)
        abs_out = os.path.abspath(output)
        # 32 is the format type for PDF
        deck = powerpoint.Presentations.Open(abs_in, WithWindow=False)
        deck.SaveAs(abs_out, 32)
        deck.Close()
        powerpoint.Quit()
        return output
    finally:
        pythoncom.CoUninitialize()

def excel_to_pdf(file_path):
    pythoncom.CoInitialize()
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}.pdf")
        abs_in = os.path.abspath(file_path)
        abs_out = os.path.abspath(output)
        # 0 is xlTypePDF
        wb = excel.Workbooks.Open(abs_in)
        wb.ExportAsFixedFormat(0, abs_out)
        wb.Close(False)
        excel.Quit()
        return output
    finally:
        pythoncom.CoUninitialize()

def image_to_pdf(file_path):
    output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}.pdf")
    # Using PyMuPDF (fitz) for robust image to PDF conversion
    doc = fitz.open()
    img_doc = fitz.open(file_path)
    pdfbytes = img_doc.convert_to_pdf()
    img_doc.close()
    
    img_pdf = fitz.open("pdf", pdfbytes)
    doc.insert_pdf(img_pdf)
    img_pdf.close()
    
    doc.save(output)
    doc.close()
    return output

def pdf_to_images(file_path):
    doc = fitz.open(file_path)
    outputs = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=150)
        output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}_page_{page_num+1}.png")
        pix.save(output)
        outputs.append(output)
    doc.close()
    return outputs

# ========== NEW PDF OPERATIONS (Using PyMuPDF) ==========
def open_and_view_pdf(file_path):
    doc = fitz.open(file_path)
    result = {
        "total_pages": len(doc),
        "metadata": doc.metadata,
        "text": "".join([page.get_text() for page in doc])
    }
    doc.close()
    return result

def merge_pdfs(pdf_paths):
    result = fitz.open()
    for path in pdf_paths:
        doc = fitz.open(path)
        result.insert_pdf(doc)
        doc.close()
    output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}.pdf")
    result.save(output)
    result.close()
    return output

def split_pdf(file_path):
    doc = fitz.open(file_path)
    outputs = []
    for page_num in range(len(doc)):
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}_page_{page_num+1}.pdf")
        new_doc.save(output)
        new_doc.close()
        outputs.append(output)
    doc.close()
    return outputs

def delete_pages(file_path, pages_to_delete):
    doc = fitz.open(file_path)
    # Delete in reverse order
    for page_num in sorted(pages_to_delete, reverse=True):
        if 1 <= page_num <= len(doc):
            doc.delete_page(page_num - 1)
    output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}.pdf")
    doc.save(output)
    doc.close()
    return output

def extract_pages(file_path, page_numbers):
    doc = fitz.open(file_path)
    new_doc = fitz.open()
    for page_num in page_numbers:
        if 1 <= page_num <= len(doc):
            new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
    output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}.pdf")
    new_doc.save(output)
    new_doc.close()
    doc.close()
    return output

def images_to_pdf(image_paths):
    images = [Image.open(path).convert("RGB") for path in image_paths]
    output = os.path.join(MEDIA_PATH, f"{uuid.uuid4()}.pdf")
    if images:
        images[0].save(output, save_all=True, append_images=images[1:])
    return output