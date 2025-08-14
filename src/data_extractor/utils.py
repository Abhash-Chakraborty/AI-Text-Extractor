"""Utility functions for data extraction."""

import re
from typing import Optional
from urllib.parse import urlparse


def is_google_drive_url(url: str) -> bool:
    """Check if URL is a Google Drive file link."""
    return 'drive.google.com' in url.lower() or 'docs.google.com' in url.lower()


def extract_google_drive_file_id(url: str) -> Optional[str]:
    """Extract file ID from Google Drive URL."""
    # Handle different Google Drive URL formats
    patterns = [
        r'/d/([a-zA-Z0-9-_]+)',  # /file/d/FILE_ID/view
        r'id=([a-zA-Z0-9-_]+)',  # ?id=FILE_ID
        r'/([a-zA-Z0-9-_]+)/edit',  # Google Docs edit URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def validate_file_type(filename: str) -> tuple[bool, str]:
    """Validate if file type is supported."""
    import os
    
    file_ext = os.path.splitext(filename)[1].lower()
    
    # Supported file types
    text_files = {'.txt', '.md', '.rtf', '.csv', '.log'}
    vision_files = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico'}
    
    if file_ext in text_files:
        return True, "text"
    elif file_ext in vision_files:
        return True, "vision"
    else:
        return False, "unsupported"
