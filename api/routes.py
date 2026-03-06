"""
API Routes — Resolve Aí

All REST endpoints. Currently:
- POST /api/chat — send a consumer situation, get CDC-based guidance
- GET  /api/health — service health check
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import settings

router = APIRouter(prefix="/api")


# --- Request / Response Models ------------------------------------------------


class ChatRequest(BaseModel):
    """User message describing a consumer situation."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        examples=["Comprei um celular e a tela quebrou com 10 dias de uso"],
    )


class ArticleRef(BaseModel):
    """Reference to a CDC article found during legal analysis."""

    number: str = Field(..., examples=["Art. 18"])
    title: str = Field(..., examples=["Responsabilidade por Vício do Produto"])
    relevance: str = Field(
        ...,
        examples=["O produto apresentou defeito dentro do prazo de garantia legal (90 dias)"],
    )


class AnalysisResult(BaseModel):
    """Structured legal analysis of the consumer's case."""

    is_cdc_case: bool
    articles: list[ArticleRef] = []
    rights: list[str] = []
    severity: str = Field(default="", examples=["low", "medium", "high"])


class ChatResponse(BaseModel):
    """Complete response to the consumer, with analysis and sources."""

    response: str
    analysis: AnalysisResult | None = None
    sources: list[str] = []
    metadata: dict = {}


class HealthResponse(BaseModel):
    """Service health check response."""

    status: str
    version: str
    llm_provider: str
    vector_store: str


# --- Endpoints ----------------------------------------------------------------


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Analyze a consumer situation and return CDC-based guidance.

    This is a stub that returns a placeholder response.
    It will be connected to the LangGraph agent pipeline in the next sprint.
    """
    # TODO: replace with actual agent pipeline call
    return ChatResponse(
        response=(
            "👋 Olá! O Resolve Aí está em construção. "
            "Em breve, vou analisar sua situação com base no Código de Defesa do Consumidor. "
            f'Você disse: "{request.message}"'
        ),
        analysis=None,
        sources=[],
        metadata={"model": "stub", "version": "0.1.0"},
    )


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Service health check — confirms the API is running and shows config."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        llm_provider=settings.llm_provider,
        vector_store=settings.vector_store,
    )
