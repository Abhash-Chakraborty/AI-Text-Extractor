---
title: Text_Extractor
emoji: 📖
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
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
- uv package manager (recommended) or pip

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Abhash-Chakraborty/Darzi-AI-Resume-Suite.git
   cd Darzi-AI-Resume-Suite/backend/data-extractor
   ```

2. **Install with uv** (recommended):
   ```bash
   uv sync
   ```
   
   Or with pip:
   ```bash
   pip install -e .
   ```

3. **Set up Google Vision API**:
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
# from the project root
streamlit run src/streamlit_app.py
```

Then open http://localhost:8501 in your browser to:
- Upload PDF files or text documents
- Paste Google Drive links
- Extract and download text content

### API Endpoints

The Streamlit app also provides API endpoints:

#### Extract Text from File Upload

```bash
curl -X POST "http://localhost:8501/api/extract" \
  -F "file=@your_document.pdf"
```

#### Extract Text from URL

```bash
curl -X POST "http://localhost:8501/api/extract-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://drive.google.com/file/d/your-file-id/view"}'
```

### Python Package

```python
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

1. **Push to Hugging Face**:
   ```bash
   git push https://huggingface.co/spaces/YOUR_USERNAME/data-extractor
   ```

2. **Add a Secret in your Space settings**:
   - `GOOGLE_API_KEY`: Your Google Vision API key

3. **The app will auto-deploy** and be available as both a web interface and API

### Local Development

```bash
# Install development dependencies
uv sync --group dev

# Run tests
pytest

# Format code
black src/
isort src/

# Lint code
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
├── src/streamlit_app.py # Streamlit web app
├── pyproject.toml       # Package configuration
├── requirements.txt     # Dependencies for HF Spaces
└── README.md           # This file
```

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
- 🐛 Issues: [GitHub Issues](https://github.com/Abhash-Chakraborty/Darzi-AI-Resume-Suite/issues)
- 💬 LinkedIn: [Abhash Chakraborty](https://www.linkedin.com/in/abhash-chakraborty-b78862247)
