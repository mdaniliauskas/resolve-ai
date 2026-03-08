# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev

# Copy application code
COPY agents/ agents/
COPY config.py .
COPY frontend/ frontend/
COPY rag/ rag/

# Copy the local vector database so it's baked into the image
# This avoids needing a separate database service for the MVP
COPY data/chroma_db/ data/chroma_db/
COPY data/cdc/ data/cdc/

# Expose Gradio's port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
# Cloud Run sets PORT dynamically, but Gradio uses 7860 by default in app.py
# We can tell Gradio to use the PORT env var via GRADIO_SERVER_PORT
ENV GRADIO_SERVER_PORT=8080
EXPOSE 8080

# Run the Gradio App
CMD ["python", "-m", "frontend.app"]
