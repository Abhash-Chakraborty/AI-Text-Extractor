"""FastAPI app exposing text extraction endpoints."""

import os
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, AnyHttpUrl

import sys
import os as _os
sys.path.insert(0, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..')))

from data_extractor import extract_text
from data_extractor.utils import validate_file_type, format_file_size


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


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/api/extract")
async def extract_from_file(file: UploadFile = File(...)):
    # Validate file type
    is_valid, file_type = validate_file_type(file.filename)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")

    # Ensure API key for vision types
    if file_type == "vision" and not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(status_code=400, detail="Missing GOOGLE_API_KEY for PDFs/images")

    # Persist to temp and extract
    suffix = os.path.splitext(file.filename)[1]
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
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
        raise HTTPException(status_code=500, detail=str(e))
