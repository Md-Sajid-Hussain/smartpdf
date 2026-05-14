import os
import uuid
import zipfile
import json
import re
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import fitz  # PyMuPDF
import spacy
from datetime import datetime

# Media path
from django.conf import settings
MEDIA_PATH = settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'media')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Session storage
sessions = {}

class PDFSplitter:
    def __init__(self, session_id, pdf_path, total_pages):
        self.session_id = session_id
        self.pdf_path = pdf_path
        self.total_pages = total_pages
        self.current_result = None
        self.last_operation = None
        
    @staticmethod
    def parse_command_with_spacy(command_text):
        """Parse natural language command using spaCy"""
        command_lower = command_text.lower()
        
        # First, extract page ranges directly from the command text
        ranges = PDFSplitter.extract_page_ranges(command_text)
        
        # Detect intent based on keywords
        intent = None
        group_size = None
        
        # Intent 1: Single pages
        single_keywords = ['single page', 'each page', 'page by page', 'separate page', 'individual page', 'every page', 'split all pages', 'all pages separately']
        if any(keyword in command_lower for keyword in single_keywords):
            intent = 'single_pages'
        
        # Intent 2: Two equal parts
        elif '2 parts' in command_lower or 'two parts' in command_lower or 'divide into 2' in command_lower or 'split in half' in command_lower:
            intent = 'two_parts'
        
        # Intent 3: Group by N pages
        elif 'group' in command_lower and ('page' in command_lower or 'pages' in command_lower):
            intent = 'group_by_n'
            # Extract numbers using regex
            numbers = re.findall(r'\d+', command_text)
            if numbers:
                group_size = int(numbers[0])
        
        # Intent 4: Extract specific pages/ranges
        elif ('extract' in command_lower or 'get' in command_lower) and ('page' in command_lower or 'pages' in command_lower):
            intent = 'extract_pages'
        
        # Intent 5: Split by custom ranges
        elif 'split as ranges' in command_lower or 'split by ranges' in command_lower or 'custom ranges' in command_lower:
            intent = 'custom_ranges'
        elif 'split as' in command_lower and 'range' in command_lower:
            intent = 'custom_ranges'
        
        # Intent 6: Remove/Delete pages
        elif 'remove' in command_lower or 'delete' in command_lower:
            intent = 'remove_pages'
        
        # Handle single number or simple split
        elif re.match(r'^\d+\s*-\s*\d+$', command_text.strip()):
            # Just a range like "1-5" - treat as custom range
            intent = 'custom_ranges'
            ranges = PDFSplitter.extract_page_ranges(command_text)
        
        return {
            'intent': intent,
            'group_size': group_size,
            'ranges': ranges,
        }
    
    @staticmethod
    def extract_page_ranges(text):
        """Extract page ranges from text like '1,3,5,7' or '1-5,10-15'"""
        ranges = []
        
        # Find all number patterns (including ranges)
        # Pattern matches: 1, 12, 1-5, 10-15, etc.
        # Also matches comma-separated lists
        parts = re.split(r'[,;]\s*', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if it's a range (contains hyphen)
            if '-' in part:
                range_match = re.match(r'(\d+)\s*-\s*(\d+)', part)
                if range_match:
                    start = int(range_match.group(1))
                    end = int(range_match.group(2))
                    if start <= end:
                        ranges.append(('range', start, end))
                    else:
                        ranges.append(('range', end, start))
            else:
                # Try to extract individual numbers
                numbers = re.findall(r'\b\d+\b', part)
                for num_str in numbers:
                    try:
                        page_num = int(num_str)
                        ranges.append(('single', page_num, page_num))
                    except ValueError:
                        continue
        
        # Also check the entire text for patterns like "1-5" without commas
        if not ranges:
            range_match = re.search(r'(\d+)\s*-\s*(\d+)', text)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                if start <= end:
                    ranges.append(('range', start, end))
                else:
                    ranges.append(('range', end, start))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_ranges = []
        for r in ranges:
            key = (r[0], r[1], r[2])
            if key not in seen:
                seen.add(key)
                unique_ranges.append(r)
        
        print(f"Extracted ranges: {unique_ranges}")  # Debug log
        return unique_ranges
    
    def split_single_pages(self):
        """Split into individual pages"""
        doc = fitz.open(self.pdf_path)
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
        
        zip_path = self.create_zip(output_files, "single_pages")
        
        return {
            'success': True,
            'message': f"✅ Split into {len(output_files)} individual pages",
            'files': output_files,
            'zip_path': zip_path,
            'single_pdf': None
        }
    
    def split_two_parts(self):
        """Split into two equal/almost equal parts"""
        doc = fitz.open(self.pdf_path)
        half = self.total_pages // 2
        first_half_pages = half if self.total_pages % 2 == 0 else half + 1
        
        output_files = []
        
        # First part
        part1 = fitz.open()
        part1.insert_pdf(doc, from_page=0, to_page=first_half_pages - 1)
        part1_path = os.path.join(MEDIA_PATH, f"part1_{uuid.uuid4()}.pdf")
        part1.save(part1_path)
        part1.close()
        output_files.append(part1_path)
        
        # Second part
        part2 = fitz.open()
        part2.insert_pdf(doc, from_page=first_half_pages, to_page=self.total_pages - 1)
        part2_path = os.path.join(MEDIA_PATH, f"part2_{uuid.uuid4()}.pdf")
        part2.save(part2_path)
        part2.close()
        output_files.append(part2_path)
        
        doc.close()
        
        zip_path = self.create_zip(output_files, "two_parts")
        
        return {
            'success': True,
            'message': f"✅ Split into 2 parts: Part 1 ({first_half_pages} pages), Part 2 ({self.total_pages - first_half_pages} pages)",
            'files': output_files,
            'zip_path': zip_path,
            'single_pdf': None
        }
    
    def split_group_by_n(self, group_size):
        """Split into groups of N pages"""
        if not group_size or group_size <= 0:
            return {'success': False, 'message': 'Invalid group size'}
        
        doc = fitz.open(self.pdf_path)
        output_files = []
        group_num = 1
        
        for start_page in range(0, self.total_pages, group_size):
            end_page = min(start_page + group_size, self.total_pages) - 1
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
            output_filename = f"group_{group_num}_{uuid.uuid4()}.pdf"
            output_path = os.path.join(MEDIA_PATH, output_filename)
            new_doc.save(output_path)
            new_doc.close()
            output_files.append(output_path)
            group_num += 1
        
        doc.close()
        
        zip_path = self.create_zip(output_files, f"groups_of_{group_size}")
        
        return {
            'success': True,
            'message': f"✅ Split into {len(output_files)} groups of {group_size} pages (last group may have fewer pages)",
            'files': output_files,
            'zip_path': zip_path,
            'single_pdf': None
        }
    
    def extract_pages(self, ranges):
        """Extract specific pages/ranges into single PDF"""
        if not ranges:
            return {'success': False, 'message': 'No valid page ranges provided'}
        
        print(f"Extracting pages from ranges: {ranges}")  # Debug log
        
        doc = fitz.open(self.pdf_path)
        new_doc = fitz.open()
        pages_to_extract = set()
        
        for range_type, start, end in ranges:
            if 1 <= start <= self.total_pages:
                for page_num in range(start, end + 1):
                    if 1 <= page_num <= self.total_pages:
                        pages_to_extract.add(page_num - 1)  # Convert to 0-index
        
        if not pages_to_extract:
            return {'success': False, 'message': 'No valid pages to extract'}
        
        for page_num in sorted(pages_to_extract):
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        doc.close()
        
        output_path = os.path.join(MEDIA_PATH, f"extracted_{uuid.uuid4()}.pdf")
        new_doc.save(output_path)
        new_doc.close()
        
        return {
            'success': True,
            'message': f"✅ Extracted {len(pages_to_extract)} pages into single PDF",
            'files': [output_path],
            'zip_path': None,
            'single_pdf': output_path
        }
    
    def split_custom_ranges(self, ranges):
        """Split by custom non-overlapping ranges into multiple PDFs"""
        if not ranges:
            return {'success': False, 'message': 'No valid ranges provided'}
        
        print(f"Splitting custom ranges: {ranges}")  # Debug log
        
        # Sort ranges by start page
        ranges.sort(key=lambda x: x[1])
        
        doc = fitz.open(self.pdf_path)
        output_files = []
        range_num = 1
        
        for range_type, start, end in ranges:
            if 1 <= start <= self.total_pages and 1 <= end <= self.total_pages:
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start-1, to_page=end-1)
                output_path = os.path.join(MEDIA_PATH, f"range_{range_num}_{uuid.uuid4()}.pdf")
                new_doc.save(output_path)
                new_doc.close()
                output_files.append(output_path)
                range_num += 1
        
        doc.close()
        
        if not output_files:
            return {'success': False, 'message': 'No valid ranges to split'}
        
        zip_path = self.create_zip(output_files, "custom_ranges")
        
        return {
            'success': True,
            'message': f"✅ Split into {len(output_files)} PDFs based on custom ranges",
            'files': output_files,
            'zip_path': zip_path,
            'single_pdf': None
        }
    
    def remove_pages(self, ranges):
        """Remove specific pages and return remaining as single PDF"""
        if not ranges:
            return {'success': False, 'message': 'No valid pages to remove'}
        
        doc = fitz.open(self.pdf_path)
        new_doc = fitz.open()
        pages_to_remove = set()
        
        for range_type, start, end in ranges:
            for page_num in range(start, end + 1):
                pages_to_remove.add(page_num - 1)
        
        for page_num in range(self.total_pages):
            if page_num not in pages_to_remove:
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        doc.close()
        
        output_path = os.path.join(MEDIA_PATH, f"remaining_{uuid.uuid4()}.pdf")
        new_doc.save(output_path)
        new_doc.close()
        
        removed_count = len(pages_to_remove)
        remaining_count = self.total_pages - removed_count
        
        return {
            'success': True,
            'message': f"✅ Removed {removed_count} pages, {remaining_count} pages remaining",
            'files': [output_path],
            'zip_path': None,
            'single_pdf': output_path
        }
    
    def create_zip(self, file_paths, prefix):
        """Create ZIP archive from list of files"""
        zip_filename = f"{prefix}_{uuid.uuid4()}.zip"
        zip_path = os.path.join(MEDIA_PATH, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i, file_path in enumerate(file_paths):
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname=arcname)
        
        return zip_path
    
    def cleanup_files(self):
        """Clean up temporary files"""
        try:
            if self.current_result:
                for file_path in self.current_result.get('files', []):
                    if os.path.exists(file_path):
                        os.remove(file_path)
                if self.current_result.get('zip_path') and os.path.exists(self.current_result['zip_path']):
                    os.remove(self.current_result['zip_path'])
                if self.current_result.get('single_pdf') and os.path.exists(self.current_result['single_pdf']):
                    os.remove(self.current_result['single_pdf'])
        except Exception as e:
            print(f"Cleanup error: {e}")


@csrf_exempt
@require_http_methods(["POST"])
def upload_pdf_api(request):
    """Upload PDF and create session"""
    try:
        pdf_file = request.FILES.get('pdf')
        if not pdf_file:
            return JsonResponse({"error": "PDF file required"}, status=400)
        
        session_id = str(uuid.uuid4())
        temp_filename = f"upload_{session_id}.pdf"
        temp_path = default_storage.save(temp_filename, ContentFile(pdf_file.read()))
        temp_full_path = default_storage.path(temp_path)
        
        doc = fitz.open(temp_full_path)
        total_pages = len(doc)
        doc.close()
        
        sessions[session_id] = PDFSplitter(session_id, temp_full_path, total_pages)
        
        return JsonResponse({
            "success": True,
            "session_id": session_id,
            "total_pages": total_pages,
            "message": f"PDF uploaded successfully with {total_pages} pages"
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def split_command_api(request):
    """Process split command using NLP"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        command = data.get('command')
        
        if not session_id or not command:
            return JsonResponse({"error": "session_id and command required"}, status=400)
        
        if session_id not in sessions:
            return JsonResponse({"error": "Invalid session. Please upload PDF again."}, status=400)
        
        splitter = sessions[session_id]
        
        # Handle confirmation if needed
        if command.lower() == 'confirm':
            if splitter.last_operation and splitter.last_operation.get('needs_confirmation'):
                pending = splitter.last_operation
                result = pending['execute_func']()
                splitter.current_result = result
                splitter.last_operation = None
                return JsonResponse({
                    "success": True,
                    "message": result['message'],
                    "download_ready": True
                })
            else:
                return JsonResponse({"error": "No pending operation to confirm"}, status=400)
        
        elif command.lower() == 'cancel':
            splitter.last_operation = None
            return JsonResponse({
                "success": True,
                "message": "Operation cancelled"
            })
        
        # Parse command
        parsed = PDFSplitter.parse_command_with_spacy(command)
        intent = parsed['intent']
        ranges = parsed['ranges']
        group_size = parsed['group_size']
        
        print(f"Intent: {intent}, Ranges: {ranges}, Group Size: {group_size}")  # Debug log
        
        # Execute command based on intent
        if intent == 'single_pages':
            result = splitter.split_single_pages()
            splitter.current_result = result
            return JsonResponse({
                "success": True,
                "message": result['message'],
                "download_ready": True
            })
        
        elif intent == 'two_parts':
            result = splitter.split_two_parts()
            splitter.current_result = result
            return JsonResponse({
                "success": True,
                "message": result['message'],
                "download_ready": True
            })
        
        elif intent == 'group_by_n':
            if not group_size:
                return JsonResponse({
                    "needs_confirmation": True,
                    "message": "Please specify group size. Example: 'group every 3 pages' or 'group by 5 pages'"
                })
            
            # Calculate groups
            num_groups = (splitter.total_pages + group_size - 1) // group_size
            last_group_size = splitter.total_pages % group_size
            
            if last_group_size != 0 and last_group_size != group_size and splitter.total_pages > group_size:
                groups_list = [str(group_size)] * (num_groups - 1) + [str(last_group_size)]
                warning = f"⚠️ {splitter.total_pages} pages into groups of {group_size} will be: {', '.join(groups_list)} pages.\n\nType 'confirm' to proceed or 'cancel' to abort."
                
                def execute_group():
                    return splitter.split_group_by_n(group_size)
                
                splitter.last_operation = {
                    'needs_confirmation': True,
                    'execute_func': execute_group
                }
                return JsonResponse({
                    "needs_confirmation": True,
                    "message": warning
                })
            
            result = splitter.split_group_by_n(group_size)
            splitter.current_result = result
            return JsonResponse({
                "success": True,
                "message": result['message'],
                "download_ready": True
            })
        
        elif intent == 'extract_pages':
            if not ranges:
                return JsonResponse({
                    "needs_confirmation": True,
                    "message": "Please specify pages to extract. Examples:\n• 'extract pages 1,3,5,7'\n• 'extract pages 1-10'\n• 'extract 2,4,6,8'"
                })
            result = splitter.extract_pages(ranges)
            if result['success']:
                splitter.current_result = result
                return JsonResponse({
                    "success": True,
                    "message": result['message'],
                    "download_ready": True
                })
            else:
                return JsonResponse({"error": result['message']}, status=400)
        
        elif intent == 'custom_ranges':
            if not ranges:
                # Try to extract ranges from the entire command
                ranges = PDFSplitter.extract_page_ranges(command)
                if not ranges:
                    return JsonResponse({
                        "needs_confirmation": True,
                        "message": "Please specify ranges. Examples:\n• 'split as ranges 1-5,6-10,11-15'\n• '1-5,6-10'\n• 'split as 1-3,4-7'"
                    })
            
            result = splitter.split_custom_ranges(ranges)
            if result['success']:
                splitter.current_result = result
                return JsonResponse({
                    "success": True,
                    "message": result['message'],
                    "download_ready": True
                })
            else:
                return JsonResponse({"error": result['message']}, status=400)
        
        elif intent == 'remove_pages':
            if not ranges:
                return JsonResponse({
                    "needs_confirmation": True,
                    "message": "Please specify pages to remove. Example: 'remove pages 3-5' or 'delete pages 1,2,3'"
                })
            result = splitter.remove_pages(ranges)
            if result['success']:
                splitter.current_result = result
                return JsonResponse({
                    "success": True,
                    "message": result['message'],
                    "download_ready": True
                })
            else:
                return JsonResponse({"error": result['message']}, status=400)
        
        else:
            # Try to interpret simple range
            if ranges:
                # Assume it's a custom range operation
                result = splitter.split_custom_ranges(ranges)
                if result['success']:
                    splitter.current_result = result
                    return JsonResponse({
                        "success": True,
                        "message": result['message'],
                        "download_ready": True
                    })
            
            # Show help message
            return JsonResponse({
                "needs_confirmation": True,
                "message": """I didn't understand that command. Here are examples:

📄 "split into single pages"
✂️ "divide into 2 equal parts"
📚 "group every 3 pages"
🎯 "extract pages 1,3,5,7"
🔧 "split as ranges 1-5,6-10,11-15"
🗑️ "remove pages 5-10"

Simply type the command or use the dropdown menu!"""
            })
        
    except Exception as e:
        print(f"Error in split_command_api: {str(e)}")  # Debug log
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def download_pdf_api(request, session_id):
    """Download result as single PDF"""
    try:
        if session_id not in sessions:
            return JsonResponse({"error": "Invalid session"}, status=400)
        
        splitter = sessions[session_id]
        if not splitter.current_result or not splitter.current_result.get('single_pdf'):
            return JsonResponse({"error": "No single PDF available for download"}, status=400)
        
        pdf_path = splitter.current_result['single_pdf']
        if not os.path.exists(pdf_path):
            return JsonResponse({"error": "File not found"}, status=404)
        
        return FileResponse(
            open(pdf_path, 'rb'),
            content_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="split_result.pdf"'}
        )
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def download_zip_api(request, session_id):
    """Download result as ZIP archive"""
    try:
        if session_id not in sessions:
            return JsonResponse({"error": "Invalid session"}, status=400)
        
        splitter = sessions[session_id]
        if not splitter.current_result or not splitter.current_result.get('zip_path'):
            return JsonResponse({"error": "No ZIP archive available for download"}, status=400)
        
        zip_path = splitter.current_result['zip_path']
        if not os.path.exists(zip_path):
            return JsonResponse({"error": "File not found"}, status=404)
        
        return FileResponse(
            open(zip_path, 'rb'),
            content_type='application/zip',
            headers={'Content-Disposition': f'attachment; filename="split_result.zip"'}
        )
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def cleanup_session_api(request, session_id):
    """Clean up session files"""
    try:
        if session_id in sessions:
            sessions[session_id].cleanup_files()
            del sessions[session_id]
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)