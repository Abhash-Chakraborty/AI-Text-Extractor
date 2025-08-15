---
title: Text_Extractor
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
python_version: 3.10
license: mit
short_description: Extract text from PDFs and documents using Google Vision API
---

# Data Extractor

A powerful text extraction tool that uses Google Vision API to extract text from PDFs and documents. Features a Streamlit web interface for easy file uploads and API endpoints for integration.

## Features

- 📄 **PDF Text Extraction**: Extract text from PDF files using Google Vision API
- 📝 **Text File Support**: Direct reading of text files (no API cost)
- 🔗 **Google Drive Integration**: Download and process files from Google Drive links
- 🌐 **Streamlit Web Interface**: User-friendly web app for file uploads
- 🚀 **API Endpoints**: REST API for integration with other services
- 💰 **Cost Optimized**: Text files read directly, Vision API only for PDFs/images

## Supported File Types

| File Type | Processing Method | API Cost |
|-----------|------------------|----------|
| `.pdf` | Google Vision API | ✅ Paid |
| `.txt`, `.md`, `.csv`, `.log` | Direct reading | ❌ Free |
| `.png`, `.jpg`, `.jpeg`, `.gif` | Google Vision API | ✅ Paid |
| Google Drive URLs | Auto-detect & process | Varies |

## LinkedIn Profile Processing

⚠️ **Important Note**: LinkedIn has strict anti-scraping measures. For LinkedIn profile data extraction:

1. **Download your LinkedIn profile as PDF**:
   - Go to your LinkedIn profile
   - Click "More" → "Save to PDF" 
   - Download the generated PDF file
   
2. **Upload the PDF to this tool** instead of providing LinkedIn URLs

This approach is more reliable and respects LinkedIn's terms of service.

## Setup

### Prerequisites

- Python 3.8+
- Google Cloud Vision API key
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/) (recommended for fast, reliable dependency management)

### Installation

1. **Install uv** (if not already installed):
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or with pip
   pip install uv
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/Abhash-Chakraborty/AI-Text-Extractor.git
   cd AI-Text-Extractor
   ```

3. **Install dependencies with uv** (recommended):
   ```bash
   uv sync
   ```
   
   Alternative installation methods:
   ```bash
   # With pip (slower)
   pip install -e .
   
   # For development with linting/testing tools
   uv sync --group dev
   ```

4. **Set up Google Vision API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Vision API
   - Create an API key
   - Locally: add to your environment or a `.env` file in the project root (the app reads `os.getenv('GOOGLE_API_KEY')`):
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```
   - On Hugging Face Spaces: add `GOOGLE_API_KEY` as a Secret in your Space (Settings → Secrets)

## Usage

### Streamlit Web App

Launch the web interface:

```bash
# Activate the uv environment and run Streamlit
uv run streamlit run src/streamlit_app.py

# Or from the project root (if environment is already activated)
streamlit run src/streamlit_app.py
```

Then open http://localhost:8501 in your browser to:
 - Upload PDF files or text documents
 - Paste Google Drive links
 - Extract and download text content

### REST API (FastAPI)

Run API locally with Uvicorn:

```bash
# Using uv (recommended)
uv run uvicorn src.api_app:app --reload --host 0.0.0.0 --port 8000

# Or with uvicorn directly (if environment is activated)
uvicorn src.api_app:app --reload --host 0.0.0.0 --port 8000
```

Test endpoints:

```bash
# File upload
curl -X POST "http://localhost:8000/api/extract" -F "file=@path/to/document.pdf"

# From URL
curl -X POST "http://localhost:8000/api/extract-url" \
   -H "Content-Type: application/json" \
   -d '{"url": "https://drive.google.com/file/d/FILE_ID/view"}'
```

Interactive docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Docker API mode:

```bash
docker build -t text-extractor:latest .
docker run --rm -p 8000:7860 -e APP_MODE=api --env-file .env text-extractor:latest
# now API is available at http://localhost:8000
```

Enable CORS (for browser integrations): set a comma-separated list of allowed origins

```bash
# allow any origin (dev only)
setx API_CORS_ORIGINS "*"

# or restrict to specific origins
setx API_CORS_ORIGINS "https://your-frontend.app,https://another.app"
```

### API Endpoints (FastAPI)

When running the FastAPI server, the following endpoints are available:

- GET / — Project information and usage guide
- POST /api/extract — multipart form-data file upload
- POST /api/extract-url — JSON body { "url": "<google-drive-url>" }
- GET /healthz — health check

Docs:
- GET /docs — Swagger UI
- GET /redoc — ReDoc

### Python Package

```python
# Install the package in development mode
# uv sync  # (if using uv)
# or pip install -e .

from data_extractor import extract_text

# Extract from local file
text = extract_text("path/to/document.pdf")

# Extract from Google Drive URL
text = extract_text("https://drive.google.com/file/d/FILE_ID/view")

print(text)
```

## Deployment

### Hugging Face Spaces

This app can be deployed on Hugging Face Spaces (Docker):

#### 🤖 **Automatic Deployment (Recommended)**

This repository includes GitHub Actions for automatic deployment:

1. **Set up auto-deployment** (one-time setup):
   - See [Auto-Deploy Setup Guide](.github/DEPLOY_SETUP.md)
   - Add your Hugging Face token as `HF_TOKEN` secret in GitHub
   - Push to `main` branch → automatically deploys to HF Spaces!

#### 📖 **Manual Deployment**

1. **Push to Hugging Face**:
   ```bash
   git push https://huggingface.co/spaces/abhash-chakraborty/text_extractor
   ```

2. **Configure Variables & Secrets**:
   - Variable: `APP_MODE=ui` for Streamlit UI or `APP_MODE=api` for REST API
   - Secret: `GOOGLE_API_KEY` — Your Google Vision API key (required for PDFs/images)
   - Variable (optional): `API_CORS_ORIGINS` — Comma-separated origins or `*`

3. **Access**: Use the Space URL shown on your Space page. For API mode, append the endpoints listed above.

#### Hugging Face Space endpoints (API mode)

Use the Hugging Face Space URL: `https://huggingface.co/spaces/abhash-chakraborty/text_extractor`

Examples:

```bash
# Health check
curl -sS https://abhash-chakraborty-text-extractor.hf.space/healthz

# Upload a file (PDF/txt/etc.)
curl -X POST "https://abhash-chakraborty-text-extractor.hf.space/api/extract" -F "file=@path/to/document.pdf"

# Extract from a URL (e.g., Google Drive link)
curl -X POST "https://abhash-chakraborty-text-extractor.hf.space/api/extract-url" \
   -H "Content-Type: application/json" \
   -d '{"url":"https://drive.google.com/file/d/FILE_ID/view"}'

# Interactive docs
# Swagger UI
start https://abhash-chakraborty-text-extractor.hf.space/docs
# ReDoc
start https://abhash-chakraborty-text-extractor.hf.space/redoc
```

Notes:
- Endpoints are available only when the Space runs with `APP_MODE=api`.
- For browser apps hosted on a different domain, set `API_CORS_ORIGINS` in the Space Variables.
- For private Spaces, include an access token:
   - Generate a token on https://huggingface.co/settings/tokens
   - Add header: `-H "Authorization: Bearer HF_TOKEN"`

### Local Development

```bash
# Install development dependencies with uv
uv sync --group dev

# Run tests (when available)
uv run pytest

# Format code
uv run black src/
uv run isort src/

# Lint code
uv run flake8 src/

# Or use traditional tools (if environment is activated)
black src/
isort src/
flake8 src/
```

## Cost Considerations

- **Text files**: Free (direct reading)
- **PDF files**: ~$1.50 per 1,000 pages (Google Vision API)
- **Images**: ~$1.50 per 1,000 images (Google Vision API)

## File Structure

```
data-extractor/
├── src/data_extractor/
│   ├── __init__.py
│   ├── core.py          # Main extraction logic
│   └── utils.py         # Helper functions
├── src/api_app.py       # FastAPI app (REST API)
├── src/streamlit_app.py # Streamlit web app
├── pyproject.toml       # Package configuration & dependencies
├── uv.lock             # UV lock file for reproducible builds
├── Dockerfile          # Docker configuration
└── README.md           # This file
```

## Why UV?

This project uses [UV](https://docs.astral.sh/uv/) for dependency management because it's:
- **Fast**: 10-100x faster than pip
- **Reliable**: Deterministic dependency resolution
- **Simple**: Drop-in replacement for pip/virtualenv
- **Modern**: Built in Rust with excellent Python tooling integration
## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- 📧 Email: abhashchak14@gmail.com
- 💬 LinkedIn: [Abhash Chakraborty](https://www.linkedin.com/in/abhash-chakraborty-b78862247)
