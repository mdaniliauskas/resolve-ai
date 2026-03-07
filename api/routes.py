"""
API Routes — Resolve Aí

All REST endpoints:
- POST /api/chat — send a consumer situation, get CDC-based guidance
- GET  /api/health — service health check
"""

import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agents.workflow import run_chat
from config import settings

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


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


class ChannelRef(BaseModel):
    """A resolution channel in the strategy."""

    step: int
    name: str
    description: str
    link: str | None = None


class StrategyDetail(BaseModel):
    """Resolution strategy with channels and tips."""

    channels: list[ChannelRef] = []
    estimated_resolution_time: str = ""
    tips: list[str] = []


class ChatResponse(BaseModel):
    """Complete response to the consumer, with analysis and sources."""

    response: str
    analysis: AnalysisResult | None = None
    strategy: StrategyDetail | None = None
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

    Runs the full LangGraph agent pipeline: orchestrator → RAG → legal
    analysis → strategy → response formatting.
    """
    try:
        result = run_chat(request.message)
    except Exception:
        logger.exception("Agent pipeline failed for message: '%s...'", request.message[:80])
        return ChatResponse(
            response=(
                "Desculpe, ocorreu um erro ao processar sua solicitação. "
                "Por favor, tente novamente em alguns instantes."
            ),
            metadata={"error": True},
        )

    # Map workflow result to API response models
    analysis_out = None
    if result.get("analysis"):
        analysis = result["analysis"]
        analysis_out = AnalysisResult(
            is_cdc_case=analysis.is_cdc_case,
            articles=[
                ArticleRef(number=a.number, title=a.title, relevance=a.relevance)
                for a in analysis.articles
            ],
            rights=analysis.rights,
            severity=analysis.severity,
        )

    strategy_out = None
    if result.get("strategy"):
        strategy = result["strategy"]
        strategy_out = StrategyDetail(
            channels=[
                ChannelRef(step=c.step, name=c.name, description=c.description, link=c.link)
                for c in strategy.channels
            ],
            estimated_resolution_time=strategy.estimated_resolution_time,
            tips=strategy.tips,
        )

    return ChatResponse(
        response=result.get("response", ""),
        analysis=analysis_out,
        strategy=strategy_out,
        sources=result.get("sources", []),
        metadata={
            "model": settings.gemini_model,
            **result.get("metadata", {}),
        },
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
