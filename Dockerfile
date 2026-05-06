# syntax=docker/dockerfile:1
# Backend — FastAPI + LangGraph + ChromaDB
# Deployed as Cloud Run service: resolve-ai-api

FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY agents/ agents/
COPY api/ api/
COPY rag/ rag/
COPY config.py .

# Bake the vector database into the image (stateless Cloud Run)
COPY data/chroma_db/ data/chroma_db/
COPY data/cdc/ data/cdc/

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8080

EXPOSE 8080

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
