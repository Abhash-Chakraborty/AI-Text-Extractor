"""Core text extraction functionality."""

import base64
import os
import re
import tempfile
from typing import Optional, Tuple

import requests
from dotenv import load_dotenv

from .utils import is_google_drive_url, extract_google_drive_file_id

load_dotenv()


def download_google_drive_file(url: str) -> Tuple[str, str]:
    """Download file from Google Drive. Returns (temp_path, file_extension)."""
    file_id = extract_google_drive_file_id(url)
    if not file_id:
        raise ValueError("Could not extract file ID from Google Drive URL")
    
    # Use the direct download URL
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(download_url, headers=headers, timeout=60, stream=True)
        
        # Handle Google Drive's virus scan warning for large files
        if 'virus scan warning' in response.text.lower():
            # Extract the confirmation URL
            confirm_pattern = r'href="(/uc\?export=download[^"]*)"'
            match = re.search(confirm_pattern, response.text)
            if match:
                confirm_url = "https://drive.google.com" + match.group(1).replace('&amp;', '&')
                response = requests.get(confirm_url, headers=headers, timeout=60, stream=True)
        
        response.raise_for_status()
        
        # Determine file extension from content type or URL
        content_type = response.headers.get('content-type', '').lower()
        
        if 'pdf' in content_type:
            file_ext = '.pdf'
        elif 'text' in content_type:
            file_ext = '.txt'
        elif '/vnd.google-apps.document' in content_type:
            file_ext = '.txt'  # Google Docs exported as text
        else:
            # Try to guess from URL or default to .txt
            if 'pdf' in url.lower():
                file_ext = '.pdf'
            else:
                file_ext = '.txt'
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
            temp_path = temp_file.name
        
        # After downloading, check the actual file content to confirm type
        with open(temp_path, 'rb') as f:
            file_header = f.read(10)
        
        # If it looks like a PDF but we detected it as text, correct it
        if file_header.startswith(b'%PDF') and file_ext == '.txt':
            # Rename the file to have .pdf extension
            new_temp_path = temp_path.replace('.txt', '.pdf')
            os.rename(temp_path, new_temp_path)
            temp_path = new_temp_path
            file_ext = '.pdf'
        
        return temp_path, file_ext
        
    except requests.RequestException as e:
        raise RuntimeError(f"Error downloading from Google Drive: {e}")


def extract_text_vision_api(file_path: str) -> str:
    """Extract text using Google Cloud Vision API for PDFs and images."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise RuntimeError('Missing GOOGLE_API_KEY in environment variables')
    
    # Read and encode file
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    encoded_content = base64.b64encode(file_content).decode('utf-8')
    
    # Determine if it's a PDF or image
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        # For PDFs, use document text detection
        request_body = {
            "requests": [{
                "inputConfig": {
                    "content": encoded_content,
                    "mimeType": "application/pdf"
                },
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                "imageContext": {"languageHints": ["en"]}
            }]
        }
        
        url = f"https://vision.googleapis.com/v1/files:annotate?key={api_key}"
    else:
        # For images, use regular text detection
        request_body = {
            "requests": [{
                "image": {"content": encoded_content},
                "features": [{"type": "TEXT_DETECTION"}]
            }]
        }
        
        url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    
    # Make API request
    response = requests.post(url, json=request_body)
    response.raise_for_status()
    
    result = response.json()
    
    # Handle errors
    if 'error' in result:
        raise RuntimeError(f"Vision API error: {result['error']}")
    
    # Extract text from response
    if file_ext == '.pdf':
        # PDF response structure - handle nested responses
        responses = result.get('responses', [])
        if not responses:
            return ""
        
        full_text = ""
        for resp in responses:
            if 'error' in resp:
                raise RuntimeError(f"PDF processing error: {resp['error']}")
            elif 'responses' in resp:
                # Nested responses for PDF pages
                page_responses = resp['responses']
                for page_resp in page_responses:
                    if 'fullTextAnnotation' in page_resp:
                        page_text = page_resp['fullTextAnnotation'].get('text', '')
                        full_text += page_text + "\n"
                    elif 'textAnnotations' in page_resp and page_resp['textAnnotations']:
                        # Fallback to first text annotation
                        page_text = page_resp['textAnnotations'][0].get('description', '')
                        full_text += page_text + "\n"
            elif 'fullTextAnnotation' in resp:
                # Direct fullTextAnnotation (shouldn't happen for PDFs but handle it)
                full_text += resp['fullTextAnnotation'].get('text', '')
        
        return full_text.strip()
    else:
        # Image response structure
        responses = result.get('responses', [])
        if not responses:
            return ""
        
        resp = responses[0]
        if 'error' in resp:
            raise RuntimeError(f"Image processing error: {resp['error']}")
        
        if 'fullTextAnnotation' in resp:
            return resp['fullTextAnnotation'].get('text', '')
        elif 'textAnnotations' in resp and resp['textAnnotations']:
            # Fallback to first text annotation
            return resp['textAnnotations'][0].get('description', '')
        
        return ""


def read_text_file(file_path: str) -> str:
    """Read text file directly (no API needed)."""
    try:
        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read().strip()
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, read as binary and decode with errors='replace'
        with open(file_path, 'rb') as f:
            content = f.read()
            return content.decode('utf-8', errors='replace').strip()
            
    except Exception as e:
        raise RuntimeError(f"Error reading text file: {e}")


def extract_text(input_path: str) -> str:
    """Main extract function - handles local files and Google Drive links."""
    temp_file = None
    
    try:
        # Check if input is a Google Drive URL
        if input_path.startswith('http') and is_google_drive_url(input_path):
            temp_file, file_ext = download_google_drive_file(input_path)
            
            if file_ext == '.pdf':
                return extract_text_vision_api(temp_file)
            else:
                return read_text_file(temp_file)
        
        # Local file processing
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File not found: {input_path}")
        
        # Check file type
        file_ext = os.path.splitext(input_path)[1].lower()
        
        # Text files - read directly (no API cost)
        if file_ext in {'.txt', '.md', '.rtf', '.csv', '.log'}:
            return read_text_file(input_path)
        
        # PDF and image files - use Vision API
        if file_ext in {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico'}:
            return extract_text_vision_api(input_path)
        
        # Unknown file type - try to read as text first, then as binary
        try:
            return read_text_file(input_path)
        except:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    finally:
        # Clean up temporary file if created
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass
