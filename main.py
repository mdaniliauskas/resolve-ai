"""
Resolve Aí — Application Entry Point

Starts the FastAPI server. Use this for local development:

    uv run python main.py

For production, use uvicorn directly:

    uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
"""

import uvicorn

from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
