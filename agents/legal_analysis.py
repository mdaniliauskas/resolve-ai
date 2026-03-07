"""
Legal Analysis Agent — Resolve Aí

Analyzes consumer situations against the CDC using RAG context.
Identifies applicable articles, rights, and case severity.
"""

import json
import logging

from pydantic import BaseModel

from agents import llm_client
from rag.retrieval import RetrievedChunk

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """\
Você é um especialista em Direito do Consumidor brasileiro com profundo conhecimento \
do Código de Defesa do Consumidor (Lei 8.078/1990).

Com base no contexto jurídico abaixo e na situação descrita pelo consumidor, determine:

1. Se a situação se enquadra no CDC (sim/não)
2. Quais artigos são aplicáveis (liste os números e títulos)
3. Quais direitos o consumidor possui neste caso
4. A gravidade do caso: "low" (inconveniente menor), "medium" (prejuízo moderado), \
"high" (dano significativo)
5. Sua confiança na análise (0.0 a 1.0)

## Contexto Jurídico (CDC):
{rag_context}

## Situação do Consumidor:
{user_message}

## Instruções:
- Cite artigos específicos (ex: "Art. 18, §1º")
- Se não houver enquadramento claro, explique por quê
- Se a confiança for menor que 0.6, recomende consultar um advogado
- Responda SOMENTE com JSON válido, sem markdown

## Formato de resposta:
{{
  "is_cdc_case": true,
  "articles": [
    {{"number": "Art. X", "title": "...", "relevance": "..."}}
  ],
  "rights": ["Direito 1", "Direito 2"],
  "severity": "low",
  "confidence": 0.8,
  "reasoning": "Explicação breve da análise"
}}
"""


# --- Models -------------------------------------------------------------------


class ArticleDetail(BaseModel):
    """A CDC article identified as relevant to the case."""

    number: str
    title: str
    relevance: str


class LegalAnalysisResult(BaseModel):
    """Structured output from the legal analysis agent."""

    is_cdc_case: bool = False
    articles: list[ArticleDetail] = []
    rights: list[str] = []
    severity: str = "low"
    confidence: float = 0.0
    reasoning: str = ""


# --- Public API ---------------------------------------------------------------


def analyze_case(
    user_message: str, rag_chunks: list[RetrievedChunk]
) -> LegalAnalysisResult:
    """Analyze a consumer case against CDC articles retrieved by RAG.

    Sends the user message + RAG context to the LLM and parses the
    structured JSON response into a LegalAnalysisResult.
    """
    context = _format_rag_context(rag_chunks)
    prompt = ANALYSIS_PROMPT.format(rag_context=context, user_message=user_message)

    raw = llm_client.generate(prompt)
    return _parse_analysis(raw)


# --- Helpers ------------------------------------------------------------------


def _format_rag_context(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a readable context string for the LLM."""
    if not chunks:
        return "(Nenhum contexto jurídico encontrado)"

    parts = []
    for i, chunk in enumerate(chunks, 1):
        header = f"[Trecho {i}]"
        if chunk.articles:
            header += f" ({chunk.articles})"
        parts.append(f"{header}\n{chunk.text}")
    return "\n\n---\n\n".join(parts)


def _parse_analysis(raw_response: str) -> LegalAnalysisResult:
    """Parse LLM JSON response into a structured result.

    Handles common issues like markdown code fences around JSON.
    Falls back to an empty result if parsing fails.
    """
    cleaned = raw_response.strip()

    # Strip markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        data = json.loads(cleaned)
        return LegalAnalysisResult(**data)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Failed to parse LLM analysis response: %s — raw: %s...", exc, cleaned[:200])
        return LegalAnalysisResult(reasoning=f"Erro ao processar análise: {exc}")
