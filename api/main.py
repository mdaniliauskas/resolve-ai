"""
API — Resolve Aí

FastAPI application entry point. Configures middleware and mounts routes.
"""

import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown events for the application."""
    logging.basicConfig(level=settings.log_level)
    logger.info("Resolve Aí API starting (env=%s)", settings.environment)
    yield
    logger.info("Resolve Aí API shutting down")


app = FastAPI(
    title="Resolve Aí API",
    description="Multi-agent chatbot for Brazilian consumer rights (CDC)",
    version="0.1.0",
    lifespan=lifespan,
)

# --- Middleware ---------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    """Log the time each request takes — useful for spotting slow LLM calls."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s — %.0fms", request.method, request.url.path, elapsed_ms)
    return response


# --- Routes -------------------------------------------------------------------

app.include_router(router)
