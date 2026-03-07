"""
Chat Interface — Resolve Aí

Gradio-based web UI for the consumer rights chatbot.

Usage:
    uv run python -m frontend.app
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging

import gradio as gr

from agents.workflow import run_chat

logging.basicConfig(level=logging.INFO)

DISCLAIMER = (
    "⚠️ **Aviso Legal:** O Resolve Aí fornece orientações informativas com base no "
    "Código de Defesa do Consumidor (Lei 8.078/1990) e **não substitui orientação "
    "jurídica profissional**. Para casos complexos, consulte um advogado."
)

WELCOME = (
    "👋 Olá! Eu sou o **Resolve Aí**, seu assistente para questões de direito do consumidor.\n\n"
    "Descreva sua situação e eu vou analisar se seu caso se enquadra no CDC, "
    "identificar seus direitos e sugerir os melhores caminhos para resolver.\n\n"
    "**Exemplos:**\n"
    "- _Comprei um celular e a tela quebrou com 10 dias de uso_\n"
    "- _A loja se recusa a cancelar meu contrato_\n"
    "- _Cobrança indevida no meu cartão de crédito_"
)


def respond(message: str, history: list) -> str:
    """Process a user message through the agent pipeline and return the response."""
    if not message.strip():
        return "Por favor, descreva sua situação para que eu possa ajudar."

    result = run_chat(message)

    # Build response with analysis metadata when available
    response_parts = [result.get("response", "")]

    analysis = result.get("analysis")
    if analysis and analysis.is_cdc_case and analysis.articles:
        response_parts.append("\n\n---\n📋 **Artigos do CDC identificados:**")
        for article in analysis.articles:
            response_parts.append(f"- **{article.number}** — {article.title}")

    sources = result.get("sources", [])
    if sources:
        response_parts.append("\n📚 **Fontes consultadas:** " + ", ".join(sources[:3]))

    metadata = result.get("metadata", {})
    latency = metadata.get("latency_ms")
    if latency:
        response_parts.append(f"\n⏱️ _Tempo de resposta: {latency / 1000:.1f}s_")

    return "\n".join(response_parts)


# --- Build Interface ----------------------------------------------------------

THEME = gr.themes.Soft(primary_hue="blue", neutral_hue="slate")

with gr.Blocks(title="Resolve Aí — Assistente do Consumidor") as app:
    gr.Markdown("# 🛡️ Resolve Aí")
    gr.Markdown("### Seu assistente inteligente para direitos do consumidor")
    gr.Markdown(DISCLAIMER)

    chatbot = gr.ChatInterface(
        fn=respond,
        examples=[
            "Comprei um celular e a tela quebrou com 10 dias de uso",
            "A empresa se recusa a cancelar meu contrato de academia",
            "Meu nome foi colocado no SPC por uma dívida que já paguei",
            "Recebi um produto completamente diferente do anunciado",
        ],
        chatbot=gr.Chatbot(
            height=480,
            placeholder=WELCOME,
        ),
        textbox=gr.Textbox(
            placeholder="Descreva sua situação aqui...",
            max_lines=4,
        ),
    )

    gr.Markdown(
        "_Resolve Aí — Seu direito, do jeito mais fácil._ 🇧🇷 | "
        "Baseado na Lei 8.078/1990 (CDC)"
    )


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, theme=THEME)
