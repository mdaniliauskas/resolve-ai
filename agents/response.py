"""
Response Agent — Resolve Aí

Formats the final response for the consumer in clear, empathetic, actionable language.
"""

import logging

from agents import llm_client
from agents.legal_analysis import LegalAnalysisResult
from agents.strategy import StrategyResult

logger = logging.getLogger(__name__)

RESPONSE_PROMPT = """\
Você é o assistente Resolve Aí, especialista em direitos do consumidor.

Sua tarefa é formatar a resposta final para o consumidor de forma CLARA, \
EMPÁTICA e ACIONÁVEL.

## Situação do Consumidor:
{user_message}

## Análise Jurídica:
{legal_analysis}

## Estratégia de Resolução:
{strategy}

## Instruções de formatação:
- Use linguagem simples (evite juridiquês)
- Comece com empatia ("Entendemos sua situação...")
- Apresente o enquadramento legal de forma acessível
- Liste os passos de resolução numerados
- Inclua links quando disponíveis
- Termine com uma mensagem de encorajamento
- Se a confiança da análise for menor que 0.6, adicione aviso para consultar advogado
- Máximo de 400 palavras

## Tom:
- Empático mas profissional
- Claro e direto
- Encorajador ("Você TEM direitos neste caso")
"""

GREETING_RESPONSE = (
    "👋 Olá! Eu sou o **Resolve Aí**, seu assistente para questões de direito do consumidor.\n\n"
    "Me conte sua situação com um produto ou serviço e eu vou:\n"
    "1. Verificar se seu caso se enquadra no Código de Defesa do Consumidor\n"
    "2. Identificar seus direitos\n"
    "3. Sugerir os melhores caminhos para resolver\n\n"
    "⚠️ *Este é um serviço informativo e não substitui orientação jurídica profissional.*"
)

OUT_OF_SCOPE_RESPONSE = (
    "Entendo sua questão, mas ela parece estar **fora do escopo do Código de Defesa "
    "do Consumidor**.\n\n"
    "O Resolve Aí é especializado em relações de consumo (compras, serviços, "
    "contratos com empresas).\n\n"
    "Para sua situação, recomendo procurar:\n"
    "- **Defensoria Pública** do seu estado (atendimento gratuito)\n"
    "- **Ordem dos Advogados do Brasil (OAB)** — muitas seccionais oferecem "
    "atendimento pro bono\n\n"
    "Se tiver alguma dúvida sobre direitos do consumidor, estou aqui para ajudar! 😊"
)


def format_response(
    user_message: str,
    analysis: LegalAnalysisResult,
    strategy: StrategyResult,
) -> str:
    """Format the final consumer-facing response using the LLM.

    Combines the legal analysis and strategy into a clear, empathetic message.
    """
    prompt = RESPONSE_PROMPT.format(
        user_message=user_message,
        legal_analysis=analysis.model_dump_json(indent=2),
        strategy=strategy.model_dump_json(indent=2),
    )
    return llm_client.generate(prompt, temperature=0.4)


def format_greeting() -> str:
    """Return a static greeting message (no LLM call needed)."""
    return GREETING_RESPONSE


def format_out_of_scope() -> str:
    """Return a static out-of-scope message (no LLM call needed)."""
    return OUT_OF_SCOPE_RESPONSE
