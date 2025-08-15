"""FastAPI app exposing text extraction endpoints."""

import os
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, AnyHttpUrl

import sys
import os as _os
sys.path.insert(0, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..')))

from data_extractor import extract_text
from data_extractor.utils import validate_file_type, format_file_size

# File size limits (100MB max per file, 10 files max)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_FILES_COUNT = 10


class UrlPayload(BaseModel):
    url: AnyHttpUrl


app = FastAPI(title="Data Extractor API", version="0.1.0")

# CORS configuration (set API_CORS_ORIGINS to a comma-separated list, or "*" to allow all)
_cors_env = os.getenv("API_CORS_ORIGINS", "*").strip()
_allow_origins = ["*"] if _cors_env == "*" else [o.strip() for o in _cors_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint with project information."""
    return {
        "name": "Data Extractor API",
        "version": "0.1.0",
        "description": "Extract text from PDFs and documents using Google Vision API",
        "author": "Abhash Chakraborty",
        "license": "MIT",
        "features": [
            "📄 PDF Text Extraction using Google Vision API",
            "📝 Text File Support (TXT, MD, CSV, LOG) - Free",
            "🔗 Google Drive Integration",
            "🌐 REST API for integration",
            "💰 Cost Optimized - Text files read directly, Vision API only for PDFs/images"
        ],
        "supported_formats": {
            "text_files": [".txt", ".md", ".csv", ".log", ".rtf"],
            "vision_files": [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".ico"]
        },
        "limits": {
            "max_file_size": "100 MB",
            "max_files": 10,
            "note": "Optimized for resume processing (1-2 paper resumes)"
        },
        "endpoints": {
            "POST /api/extract": "Upload files for text extraction",
            "POST /api/extract-url": "Extract text from Google Drive URLs", 
            "GET /healthz": "Health check endpoint",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /redoc": "Alternative API documentation (ReDoc)"
        },
        "usage": {
            "file_upload": "curl -X POST '/api/extract' -F 'file=@document.pdf'",
            "url_extraction": "curl -X POST '/api/extract-url' -H 'Content-Type: application/json' -d '{\"url\": \"https://drive.google.com/file/d/FILE_ID/view\"}'"
        },
        "requirements": {
            "google_vision_api": "Required for PDF and image processing",
            "note": "Set GOOGLE_API_KEY environment variable"
        },
        "cost_information": {
            "text_files": "Free (direct reading)",
            "pdf_images": "~$1.50 per 1,000 pages/images (Google Vision API pricing)"
        },
        "links": {
            "documentation": "/docs",
            "alternative_docs": "/redoc",
            "github": "https://github.com/Abhash-Chakraborty/AI-Text-Extractor",
            "huggingface": "https://huggingface.co/spaces/abhash-chakraborty/text_extractor",
            "contact": "abhashchak14@gmail.com"
        }
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/api/extract")
async def extract_from_file(file: UploadFile = File(...)):
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is {format_file_size(MAX_FILE_SIZE)}. Your file is {format_file_size(file.size)}."
        )
    
    # Validate file type
    is_valid, file_type = validate_file_type(file.filename)
    if not is_valid:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file.filename}. Supported types: PDF, images (PNG, JPG, etc.), and text files (TXT, MD, CSV)."
        )

    # Ensure API key for vision types
    if file_type == "vision" and not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(
            status_code=400, 
            detail="Google Vision API key is required for PDF and image files. Please configure GOOGLE_API_KEY environment variable."
        )

    # Persist to temp and extract
    suffix = os.path.splitext(file.filename)[1]
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            
            # Double-check file size after reading
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {format_file_size(MAX_FILE_SIZE)}."
                )
            
            tmp.write(content)
            tmp_path = tmp.name

        text = extract_text(tmp_path)
        size = format_file_size(len(content))
        return JSONResponse({
            "success": True,
            "text": text,
            "file_info": {
                "name": file.filename,
                "size": size,
                "type": file_type,
            },
        })
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "Vision API error" in error_msg:
            raise HTTPException(status_code=400, detail=f"Failed to process file with Google Vision API: {error_msg}")
        elif "Google Drive" in error_msg:
            raise HTTPException(status_code=400, detail=f"Failed to download from Google Drive: {error_msg}")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to extract text: {error_msg}")
    finally:
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception:
            pass


@app.post("/api/extract-url")
async def extract_from_url(payload: UrlPayload):
    # Try extraction. It may require GOOGLE_API_KEY depending on the resource type.
    try:
        text = extract_text(str(payload.url))
        return JSONResponse({
            "success": True,
            "text": text,
            "file_info": {
                "name": "from_url",
                "size": None,
                "type": "auto",
            },
        })
    except Exception as e:
        error_msg = str(e)
        if "Vision API error" in error_msg:
            raise HTTPException(status_code=400, detail=f"Failed to process file with Google Vision API: {error_msg}")
        elif "Google Drive" in error_msg or "drive.google.com" in error_msg:
            raise HTTPException(status_code=400, detail=f"Failed to download from Google Drive: {error_msg}")
        elif "Missing GOOGLE_API_KEY" in error_msg:
            raise HTTPException(status_code=400, detail="Google Vision API key is required for PDF and image files from URLs.")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to extract text from URL: {error_msg}")
