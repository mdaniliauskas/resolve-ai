# Resolve Aí 🛡️

> **Seu assistente inteligente para dúvidas sobre o Código de Defesa do Consumidor**

A multi-agent chatbot that helps Brazilian consumers understand their rights under the *Código de Defesa do Consumidor* (CDC / Law 8.078/1990) and get concrete guidance on how to resolve their issues.

---

## The Problem

Brazilian consumers frequently **don't know whether their issue is covered by the CDC**, where to start a complaint, which channel has the best chance of resolution, or when to escalate to formal instances. The result: lost time, frustration, and unexercised rights.

## The Solution

**Resolve Aí** is an intelligent chatbot with a **multi-agent + RAG architecture** that:

1. **Analyzes** whether the case falls under the CDC and identifies applicable articles
2. **Classifies** the problem type (product defect, improper billing, false advertising, etc.)
3. **Plans** a personalized resolution strategy
4. **Guides** with concrete steps and links to the most appropriate channels

---

## Architecture

```
User → Chat Interface (Gradio)
             │
             ▼
       FastAPI REST API
             │
             ▼
    Orchestrator Agent ──→ classifies intent
       │           │
       ▼           ▼
  RAG (CDC)   Legal Analysis Agent ──→ identifies CDC articles
       │           │
       └─────┬─────┘
             ▼
      Strategy Agent ──→ builds action plan
             │
             ▼
      Response Agent ──→ formats final response
```

> Full architecture with Mermaid diagrams → [`projetos/resolve-ai/ARCHITECTURE.md`](./projetos/resolve-ai/ARCHITECTURE.md)

---

## Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Gemini 3.1 Flash Lite (Google GenAI SDK) |
| **Agent Orchestration** | LangGraph |
| **RAG / Embeddings** | ChromaDB + all-MiniLM-L6-v2 |
| **Backend** | Python 3.12 + FastAPI |
| **Frontend** | Gradio 6 |
| **Package Manager** | UV |
| **Deploy** | Docker + Google Cloud Run (planned) |

---

## Project Structure

```
resolve-ai/
├── agents/                  # AI agents (LangGraph nodes)
│   ├── llm_client.py        # Centralized Gemini SDK wrapper
│   ├── orchestrator.py      # Intent classification and routing
│   ├── legal_analysis.py    # CDC article identification via RAG
│   ├── strategy.py          # Resolution channel planning
│   ├── response.py          # Final response formatting
│   └── workflow.py          # LangGraph StateGraph orchestration
├── rag/                     # RAG pipeline
│   ├── ingest.py            # Document ingestion (download → chunk → embed → index)
│   └── retrieval.py         # Similarity search + re-ranking
├── api/                     # FastAPI backend
│   ├── main.py              # App entry point + middleware
│   └── routes.py            # /api/chat, /api/health endpoints
├── frontend/                # Gradio chat interface
│   └── app.py               # Chat UI with legal disclaimer
├── data/
│   └── cdc/                 # CDC source documents (downloaded at setup, not committed)
├── tests/                   # Unit + integration tests (32 tests)
├── evaluation/              # Golden test set (10 CDC scenarios)
├── config.py                # Single source of configuration (reads from .env)
├── pyproject.toml           # Dependencies (managed with UV)
└── .env.example             # Environment variable template
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- [UV](https://docs.astral.sh/uv/) (package manager)
- [Gemini API key](https://aistudio.google.com/) **or** [Ollama](https://ollama.com/) for local LLM

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/mdaniliauskas/resolve-ai.git
cd resolve-ai

# 2. Install dependencies (UV creates the virtualenv automatically)
uv sync

# 3. Configure environment
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# 4. Start the chat interface
uv run python frontend/app.py
# → http://localhost:7860

# Or start the API only
uv run uvicorn api.main:app --reload
# → http://localhost:8000/docs

# Run tests
uv run pytest -v
```

> Full setup guide → [`projetos/resolve-ai/SETUP.md`](./projetos/resolve-ai/SETUP.md)

---

## Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](./projetos/resolve-ai/ARCHITECTURE.md) | Detailed architecture with Mermaid diagrams |
| [MVP_SPEC.md](./projetos/resolve-ai/MVP_SPEC.md) | Technical spec: API, prompt templates, acceptance criteria |
| [TECH_DECISIONS.md](./projetos/resolve-ai/TECH_DECISIONS.md) | Architecture Decision Records (ADRs) |
| [DEVELOPMENT_GUIDE.md](./projetos/resolve-ai/DEVELOPMENT_GUIDE.md) | Dev philosophy, code patterns, and senior tips |
| [ROADMAP.md](./projetos/resolve-ai/ROADMAP.md) | Roadmap with milestones and acceptance criteria |
| [SETUP.md](./projetos/resolve-ai/SETUP.md) | Step-by-step environment setup guide |

---

## Project Status

**Current phase:** MVP (Sprint 3 complete ✅)

| Phase | Status | Description |
|---|:---:|---|
| **Sprint 1** | ✅ Done | Project scaffold, RAG pipeline, golden test set (70% precision) |
| **Sprint 2** | ✅ Done | Multi-agent pipeline (orchestrator, legal, strategy, response) |
| **Sprint 3** | ✅ Done | Gradio chat UI, legal disclaimer, README polish |
| **Enrichment** | 🔲 Planned | Case law + Advanced strategy + History + PDF |
| **Scale** | 🔲 Planned | gov.br integration + Auto-generated letters + Mobile |

---

## Legal Notice

Based on **Law 8.078/1990** (Código de Defesa do Consumidor) and SNDC regulations.

> ⚠️ Resolve Aí provides informational guidance and **does not replace professional legal counsel**. For complex cases, consulting a lawyer is recommended.

---

*Resolve Aí — Seu direito, do jeito mais fácil.* 🇧🇷
