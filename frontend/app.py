"""
Chat Interface — Resolve Aí

Gradio-based web UI (legacy — sendo substituído por Next.js na Fase A).
Mantido funcional durante a migração.
"""

import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gradio as gr

from agents.workflow import run_chat

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ── Copy ──────────────────────────────────────────────────────────────────────

HEADER_HTML = """
<div class="rz-header">
  <div class="rz-header-icon">🛡️</div>
  <div>
    <div class="rz-header-title">Resolve Aí</div>
    <div class="rz-header-subtitle">
      Seu direito, explicado de forma simples — de graça e do seu lado.
    </div>
  </div>
</div>
"""

DISCLAIMER_HTML = """
<div class="rz-disclaimer">
  <strong>⚠️ Aviso importante:</strong> O Resolve Aí orienta com base no
  Código de Defesa do Consumidor (Lei 8.078/1990) e <strong>não substitui
  um advogado</strong>. Para casos mais graves, consulte um profissional jurídico
  ou o PROCON da sua cidade — é gratuito.
</div>
"""

WELCOME = """Olá! Tô aqui pra te ajudar 👋

Me conta o que aconteceu — compra com defeito, cobrança que não deveria estar ali, \
empresa que não quer resolver, produto que não chegou... qualquer problema de consumo.

Vou analisar sua situação pelo **Código de Defesa do Consumidor** e te dizer \
exatamente **o que você tem direito** e **qual o melhor caminho pra resolver**.

💬 _Descreve o que aconteceu com você:_"""

FOOTER_HTML = """
<div class="rz-footer">
  Resolve Aí · Baseado na Lei 8.078/1990 (CDC) · 🇧🇷
</div>
"""

EXAMPLES = [
    "Comprei um celular e a tela trincou sozinha com 8 dias de uso. A loja se recusa a trocar.",
    "Meu nome foi parar no SPC por uma dívida que eu já tinha pago.",
    "A academia não quer cancelar meu contrato mesmo eu estando desempregado.",
    "Recebi um produto completamente diferente do que estava anunciado no site.",
]

# ── Theme ─────────────────────────────────────────────────────────────────────

THEME = gr.themes.Soft(
    primary_hue="emerald",
    secondary_hue="teal",
    neutral_hue="zinc",
    font=[
        gr.themes.GoogleFont("Inter"),
        "ui-sans-serif",
        "system-ui",
        "sans-serif",
    ],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"],
)

# ── CSS ───────────────────────────────────────────────────────────────────────

CUSTOM_CSS = """
/* ── Layout ───────────────────────────────────────────────────────── */
.gradio-container {
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 0 16px !important;
}

/* ── Header ───────────────────────────────────────────────────────── */
.rz-header {
    display: flex;
    align-items: center;
    gap: 16px;
    background: linear-gradient(135deg, #065f46 0%, #0d9488 100%);
    border-radius: 14px;
    padding: 22px 26px;
    margin: 12px 0 10px;
    color: white;
}

.rz-header-icon {
    font-size: 2.4rem;
    line-height: 1;
    flex-shrink: 0;
}

.rz-header-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: white;
    line-height: 1.2;
    letter-spacing: -0.5px;
}

.rz-header-subtitle {
    font-size: 0.92rem;
    color: rgba(255, 255, 255, 0.85);
    margin-top: 3px;
    line-height: 1.4;
}

/* ── Disclaimer ───────────────────────────────────────────────────── */
.rz-disclaimer {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 11px 15px;
    font-size: 0.875rem;
    color: #78350f;
    line-height: 1.55;
    margin: 4px 0 10px;
}

/* ── Chat area ────────────────────────────────────────────────────── */
.chatbot {
    border-radius: 12px !important;
    border: 1px solid #e4e4e7 !important;
}

/* User bubble */
.chatbot .message.user {
    background: #ecfdf5 !important;
    border-radius: 12px 12px 2px 12px !important;
}

/* Bot bubble */
.chatbot .message.bot {
    background: #ffffff !important;
    border: 1px solid #f0fdf4 !important;
    border-radius: 12px 12px 12px 2px !important;
}

/* ── Footer ───────────────────────────────────────────────────────── */
.rz-footer {
    text-align: center;
    font-size: 0.78rem;
    color: #a1a1aa;
    padding: 10px 0 6px;
    border-top: 1px solid #f4f4f5;
    margin-top: 6px;
}
"""

# ── Response builder ──────────────────────────────────────────────────────────


def respond(message: str, history: list) -> str:
    """Process a user message through the agent pipeline and return the response."""
    if not message.strip():
        return "Pode descrever o que aconteceu — estou aqui pra ajudar! 😊"

    result = run_chat(message)

    latency_ms = result.get("metadata", {}).get("latency_ms")
    if latency_ms:
        logger.info("request completed latency_ms=%d", latency_ms)

    parts = [result.get("response", "")]

    analysis = result.get("analysis")
    if analysis and analysis.is_cdc_case and analysis.articles:
        parts.append("\n\n---\n📋 **Artigos do CDC que amparam seu caso:**")
        for article in analysis.articles:
            parts.append(f"- **{article.number}** — {article.title}")

    if analysis and analysis.precedents:
        parts.append("\n⚖️ **Decisões do STJ sobre casos parecidos:**")
        for prec in analysis.precedents:
            parts.append(f"- **{prec.reference}**: {prec.summary}")

    sources = result.get("sources", [])
    if sources:
        parts.append("\n📚 _Fontes consultadas: " + ", ".join(sources[:3]) + "_")

    return "\n".join(parts)


# ── Interface ─────────────────────────────────────────────────────────────────

with gr.Blocks(
    title="Resolve Aí — Assistente do Consumidor",
    theme=THEME,
    css=CUSTOM_CSS,
) as app:
    gr.HTML(HEADER_HTML)
    gr.HTML(DISCLAIMER_HTML)

    gr.ChatInterface(
        fn=respond,
        examples=EXAMPLES,
        chatbot=gr.Chatbot(
            height=460,
            placeholder=WELCOME,
            show_label=False,
            bubble_full_width=False,
        ),
        textbox=gr.Textbox(
            placeholder="Descreva sua situação aqui...",
            max_lines=5,
            show_label=False,
        ),
        submit_btn="Enviar →",
        retry_btn="↺ Tentar de novo",
        undo_btn="← Voltar",
        clear_btn="🗑 Limpar",
    )

    gr.HTML(FOOTER_HTML)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    auth_credentials = None
    env_auth = os.environ.get("GRADIO_AUTH")
    if env_auth:
        user, pwd = env_auth.split(":")
        auth_credentials = (user, pwd)
    else:
        auth_credentials = ("visitante", "resolveai")

    port = int(os.environ.get("PORT", os.environ.get("GRADIO_SERVER_PORT", 7860)))

    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        theme=THEME,
        auth=auth_credentials,
        max_threads=10,
    )
