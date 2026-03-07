"""
Strategy Agent — Resolve Aí

Plans a resolution strategy with prioritized channels based on the legal analysis.
"""

import json
import logging

from pydantic import BaseModel

from agents import llm_client
from agents.legal_analysis import LegalAnalysisResult

logger = logging.getLogger(__name__)

STRATEGY_PROMPT = """\
Você é um especialista em resolução de conflitos de consumo no Brasil.

Com base na análise jurídica abaixo, sugira a melhor estratégia de resolução \
para o consumidor, priorizando a via mais rápida e menos custosa.

## Análise Jurídica:
{legal_analysis}

## Instruções:
- Sugira canais em ordem crescente de complexidade
- Para cada canal, inclua: nome, descrição prática, e link (quando disponível)
- Considere a gravidade do caso na priorização
- Se a gravidade for "high", sugira canais formais mais cedo
- Responda SOMENTE com JSON válido, sem markdown

## Formato de resposta:
{{
  "channels": [
    {{"step": 1, "name": "...", "description": "...", "link": null}}
  ],
  "estimated_resolution_time": "X dias/semanas",
  "tips": ["Dica prática 1", "Dica prática 2"]
}}
"""


# --- Models -------------------------------------------------------------------


class StrategyChannel(BaseModel):
    """A resolution channel with its step number and details."""

    step: int
    name: str
    description: str
    link: str | None = None


class StrategyResult(BaseModel):
    """Structured output from the strategy agent."""

    channels: list[StrategyChannel] = []
    estimated_resolution_time: str = ""
    tips: list[str] = []


# --- Public API ---------------------------------------------------------------


def plan_strategy(analysis: LegalAnalysisResult) -> StrategyResult:
    """Create a resolution strategy based on the legal analysis.

    Sends the analysis to the LLM to get prioritized channels and tips.
    """
    analysis_text = analysis.model_dump_json(indent=2)
    prompt = STRATEGY_PROMPT.format(legal_analysis=analysis_text)

    raw = llm_client.generate(prompt)
    return _parse_strategy(raw)


# --- Helpers ------------------------------------------------------------------


def _parse_strategy(raw_response: str) -> StrategyResult:
    """Parse LLM JSON response into a StrategyResult.

    Falls back to a default resolution ladder if parsing fails.
    """
    cleaned = raw_response.strip()

    # Strip markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        data = json.loads(cleaned)
        return StrategyResult(**data)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Failed to parse strategy response: %s — raw: %s...", exc, cleaned[:200])
        return _default_strategy()


def _default_strategy() -> StrategyResult:
    """Fallback resolution ladder when LLM parsing fails."""
    return StrategyResult(
        channels=[
            StrategyChannel(
                step=1,
                name="Contato direto com a empresa",
                description="Ligue para o SAC ou vá até a loja onde comprou",
                link=None,
            ),
            StrategyChannel(
                step=2,
                name="consumidor.gov.br",
                description="Registre sua reclamação na plataforma do governo",
                link="https://www.consumidor.gov.br",
            ),
            StrategyChannel(
                step=3,
                name="PROCON",
                description="Procure o PROCON da sua cidade ou estado",
                link=None,
            ),
        ],
        estimated_resolution_time="7-30 dias",
        tips=["Guarde todos os comprovantes e protocolos de atendimento"],
    )
