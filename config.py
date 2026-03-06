"""
Resolve Aí — Application Configuration

Single source of truth for all settings.
Values are loaded from the .env file (or environment variables).

Usage:
    from config import settings
    print(settings.api_port)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application configuration, loaded from .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # LLM provider: "gemini" or "ollama"
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # Ollama (local development)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Vector store: "chroma" or "vertex"
    vector_store: str = "chroma"
    chroma_persist_dir: str = "./data/chroma_db"

    # Google Cloud (production)
    google_project_id: str = ""
    google_region: str = "us-central1"

    # API server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: str = "http://localhost:3000"

    # App
    environment: str = "development"
    log_level: str = "INFO"

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.api_cors_origins.split(",")]


settings = Settings()
