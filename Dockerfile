FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Python path and default port (Hugging Face provides PORT)
ENV PYTHONPATH=/app/src \
    PORT=7860 \
    APP_MODE=ui

# Expose default port used by Hugging Face Spaces
EXPOSE 7860

# Health check (use PORT env set by platform)
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

# Run either Streamlit UI or FastAPI API based on APP_MODE
CMD if [ "$APP_MODE" = "api" ]; then \
    uvicorn src.api_app:app --host 0.0.0.0 --port ${PORT}; \
    else \
    streamlit run src/streamlit_app.py --server.port=${PORT} --server.address=0.0.0.0; \
    fi
