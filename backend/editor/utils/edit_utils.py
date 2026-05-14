import fitz
import os
import uuid

MEDIA_PATH = "media"

def replace_text_multiple(input_path, text_elements, page_number=0):
    """
    Inserts text at specified locations.
    text_elements is a list of dicts, each with 'text', 'x', 'y' (and optionally 'fontsize', 'color')
    """
    doc = fitz.open(input_path)
    # Ensure page_number is within bounds
    if page_number < 0 or page_number >= len(doc):
        page_number = 0
        
    page = doc[page_number]
    
    for element in text_elements:
        text = element.get('text', '')
        if not text:
            continue
            
        # coordinates
        x = float(element.get('x', 50))
        y = float(element.get('y', 50))
        # font configuration
        fontsize = float(element.get('fontsize', 12) or element.get('fontSize', 12) or 12)
        
        # Color could be passed, but default to black
        color = (0, 0, 0)
        color_val = element.get('color') or element.get('fontColor')
        if color_val:
            if isinstance(color_val, str):
                if color_val.startswith('#'):
                    # Hex color
                    color_val = color_val.lstrip('#')
                    try:
                        color = tuple(int(color_val[i:i+2], 16)/255.0 for i in (0, 2, 4))
                    except:
                        pass
                elif ',' in color_val:
                    try:
                        color = tuple(float(c)/255.0 for c in color_val.split(','))
                    except:
                        pass
            elif isinstance(color_val, list) or isinstance(color_val, tuple):
                try:
                    # check if it's 0-255 or 0-1
                    if any(c > 1.0 for c in color_val):
                        color = tuple(float(c)/255.0 for c in color_val)
                    else:
                        color = tuple(float(c) for c in color_val)
                except:
                    pass
                    
        page.insert_text(fitz.Point(x, y), text, fontsize=fontsize, color=color)
        
    os.makedirs(MEDIA_PATH, exist_ok=True)
    output_path = os.path.join(MEDIA_PATH, f"output_{uuid.uuid4()}.pdf")
    doc.save(output_path)
    doc.close()
    
    return output_path

def insert_image(input_path, image_path, x, y, width=150, height=150, page_number=0):
    """
    Inserts an image into the PDF at the specified coordinates and size.
    """
    doc = fitz.open(input_path)
    if page_number < 0 or page_number >= len(doc):
        page_number = 0
        
    page = doc[page_number]
    
    rect = fitz.Rect(x, y, x + width, y + height)
    page.insert_image(rect, filename=image_path)
    
    os.makedirs(MEDIA_PATH, exist_ok=True)
    output_path = os.path.join(MEDIA_PATH, f"output_{uuid.uuid4()}.pdf")
    doc.save(output_path)
    doc.close()
    
    return output_path

def get_pdf_info(input_path):
    """
    Returns metadata and page count of the PDF.
    """
    doc = fitz.open(input_path)
    info = {
        'page_count': len(doc),
        'metadata': doc.metadata
    }
    doc.close()
    return info