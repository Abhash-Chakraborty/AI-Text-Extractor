"""Streamlit app for Data Extractor with API endpoints."""

import io
import os
import tempfile
from typing import Dict, Any

import streamlit as st
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only for type checking; avoids runtime import of private module
    from streamlit.runtime.uploaded_file_manager import UploadedFile  # pragma: no cover

# Ensure project root is on sys.path so `src/data_extractor` is importable
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_extractor import extract_text
from data_extractor.utils import validate_file_type, format_file_size


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Data Extractor",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📄 Data Extractor")
    st.markdown("Extract text from PDFs, images, and documents using Google Vision API")
    
    # Sidebar with info
    with st.sidebar:
        st.header("ℹ️ Information")
        st.markdown("""
        **Supported Files:**
        - 📄 PDF files (Vision API)
        - 🖼️ Images (PNG, JPG, etc.)
        - 📝 Text files (TXT, MD, CSV)
        - 🔗 Google Drive links
        
        **Cost:**
        - Text files: Free
        - PDFs/Images: ~$1.50/1000 pages
        
        **LinkedIn Profiles:**
        Download as PDF from LinkedIn instead of using URLs.
        """)
        
        # API Key status
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            st.success("✅ Google Vision API configured")
        else:
            st.error("❌ Google Vision API key missing")
            st.info("Add GOOGLE_API_KEY to environment variables")
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["📁 File Upload", "🔗 URL Extract", "🔧 API"])
    
    with tab1:
        st.header("Upload Files")
        
        uploaded_files = st.file_uploader(
            "Choose files to extract text from",
            type=['pdf', 'txt', 'md', 'csv', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            accept_multiple_files=True,
            help="Upload PDFs, images, or text files"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                handle_file_upload(uploaded_file)
    
    with tab2:
        st.header("Extract from URL")
        
        url = st.text_input(
            "Google Drive URL",
            placeholder="https://drive.google.com/file/d/YOUR_FILE_ID/view",
            help="Paste a Google Drive file sharing link"
        )
        
        if st.button("Extract from URL", disabled=not url):
            handle_url_extraction(url)
    
    with tab3:
        st.header("API Endpoints")
        
        st.markdown("""
        ### REST API Usage
        
        #### 1. Extract from File Upload
        ```bash
        curl -X POST "https://your-app.hf.space/api/extract" \\
          -F "file=@document.pdf"
        ```
        
        #### 2. Extract from URL
        ```bash
        curl -X POST "https://your-app.hf.space/api/extract-url" \\
          -H "Content-Type: application/json" \\
          -d '{"url": "https://drive.google.com/file/d/FILE_ID/view"}'
        ```
        
        #### Response Format
        ```json
        {
          "success": true,
          "text": "Extracted text content...",
          "file_info": {
            "name": "document.pdf",
            "size": "1.2 MB",
            "type": "vision"
          }
        }
        ```
        """)


def handle_file_upload(uploaded_file: Any):
    """Handle individual file upload and extraction."""
    st.subheader(f"📄 {uploaded_file.name}")
    
    # Validate file type
    is_valid, file_type = validate_file_type(uploaded_file.name)
    
    if not is_valid:
        st.error(f"❌ Unsupported file type: {uploaded_file.name}")
        return
    
    # Show file info
    file_size = format_file_size(uploaded_file.size)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("File Size", file_size)
    with col2:
        st.metric("Type", file_type.title())
    with col3:
        cost = "Free" if file_type == "text" else "Vision API"
        st.metric("Cost", cost)
    
    if st.button(f"Extract Text from {uploaded_file.name}", key=f"extract_{uploaded_file.name}"):
        with st.spinner(f"Extracting text from {uploaded_file.name}..."):
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Extract text
                extracted_text = extract_text(tmp_path)
                
                # Clean up
                os.unlink(tmp_path)
                
                # Display results
                st.success(f"✅ Extracted {len(extracted_text)} characters")
                
                # Show preview and download
                show_extraction_results(extracted_text, uploaded_file.name)
                
            except Exception as e:
                st.error(f"❌ Error extracting text: {str(e)}")
                # Clean up on error
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)


def handle_url_extraction(url: str):
    """Handle URL-based extraction."""
    with st.spinner("Downloading and extracting from URL..."):
        try:
            extracted_text = extract_text(url)
            
            st.success(f"✅ Extracted {len(extracted_text)} characters from URL")
            
            # Show preview and download
            filename = f"extracted_from_url.txt"
            show_extraction_results(extracted_text, filename)
            
        except Exception as e:
            st.error(f"❌ Error extracting from URL: {str(e)}")


def show_extraction_results(text: str, filename: str):
    """Display extraction results with preview and download."""
    # Text preview
    st.subheader("📝 Preview")
    preview_length = min(1000, len(text))
    
    if len(text) > preview_length:
        st.text_area(
            "First 1000 characters:",
            text[:preview_length] + "...",
            height=200,
            disabled=True
        )
        st.info(f"Showing first {preview_length} of {len(text)} characters")
    else:
        st.text_area(
            "Extracted text:",
            text,
            height=200,
            disabled=True
        )
    
    # Download button
    st.download_button(
        label="📥 Download Full Text",
        data=text,
        file_name=f"{os.path.splitext(filename)[0]}_extracted.txt",
        mime="text/plain"
    )


# Note: API endpoints via Streamlit fragments are not used here to keep
# compatibility with older Streamlit versions on some platforms.


if __name__ == "__main__":
    main()
