FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies first for better caching
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ ./src/

# Set Python path and default port (Hugging Face provides PORT)
ENV PYTHONPATH=/app/src \
    PORT=7860 \
    APP_MODE=ui

# Expose default port used by Hugging Face Spaces
EXPOSE 7860

# Health check (use PORT env set by platform)
HEALTHCHECK CMD python -c "import requests; requests.get(f'http://localhost:{__import__('os').getenv(\"PORT\", \"7860\")}/healthz' if __import__('os').getenv('APP_MODE') == 'api' else f'http://localhost:{__import__('os').getenv(\"PORT\", \"7860\")}/_stcore/health')" || exit 1

# Run either Streamlit UI or FastAPI API based on APP_MODE
CMD if [ "$APP_MODE" = "api" ]; then \
    uvicorn src.api_app:app --host 0.0.0.0 --port ${PORT}; \
    else \
    streamlit run src/streamlit_app.py --server.port=${PORT} --server.address=0.0.0.0; \
    fi
