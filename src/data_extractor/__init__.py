"""Data Extractor - Extract text from PDFs and documents using Google Vision API."""

from .core import extract_text
from .utils import is_google_drive_url, extract_google_drive_file_id, validate_file_type, format_file_size

__version__ = "0.1.0"
__all__ = ["extract_text", "is_google_drive_url", "extract_google_drive_file_id", "validate_file_type", "format_file_size"]
