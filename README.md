# Resolve Aí 🛡️

> **Seu assistente inteligente para dúvidas sobre o Código de Defesa do Consumidor**

A multi-agent chatbot that helps Brazilian consumers understand their rights under the *Código de Defesa do Consumidor* (CDC / Law 8.078/1990) and get concrete, empathetic guidance on resolving their issues.

🔗 **Live:** https://resolve-ai-web-444080754389.southamerica-east1.run.app

---

## The Problem

Brazilian consumers frequently **don't know whether their issue is covered by the CDC**, where to start a complaint, which channel has the best chance of resolution, or when to escalate. The result: lost time, frustration, and unexercised rights.

## The Solution

**Resolve Aí** is an intelligent chatbot with a **multi-agent + RAG pipeline** that:

1. **Analyzes** whether the case falls under the CDC and identifies applicable articles
2. **Classifies** the problem type (product defect, improper billing, false advertising, etc.)
3. **Plans** a personalized resolution strategy with concrete channels and steps
4. **Responds** in empathetic, accessible language — no legal jargon

---

## Architecture

```
User → Next.js 16 (Cloud Run)
             │  SSE streaming
             ▼
       FastAPI REST API (Cloud Run)
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
      Response Agent ──→ formats final response (streaming via SSE)
```

> Full architecture with Mermaid diagrams → [`projetos/resolve-ai/ARCHITECTURE.md`](./projetos/resolve-ai/ARCHITECTURE.md)

---

## Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Gemini 3.1 Flash (Google GenAI SDK) |
| **Agent Orchestration** | LangGraph |
| **RAG / Embeddings** | ChromaDB + `gemini-embedding-001` (Cosine Distance) |
| **Backend** | Python 3.12 + FastAPI + UV |
| **Frontend** | Next.js 16 + Tailwind CSS 4 + shadcn/ui |
| **Streaming** | Server-Sent Events (SSE) |
| **Deploy** | Docker + Google Cloud Run (`southamerica-east1`) |

---

## Project Structure

```
resolve-ai/
├── agents/                  # LangGraph pipeline nodes
│   ├── llm_client.py        # Centralized Gemini SDK wrapper
│   ├── orchestrator.py      # Intent classification and routing
│   ├── legal_analysis.py    # CDC article identification via RAG
│   ├── strategy.py          # Resolution channel planning
│   ├── response.py          # Final response formatting
│   └── workflow.py          # StateGraph + SSE streaming
├── rag/                     # RAG pipeline
│   ├── ingest.py            # Download → chunk → embed → index
│   └── retrieval.py         # Similarity search + re-ranking
├── api/                     # FastAPI backend
│   ├── main.py              # App entry point + CORS middleware
│   └── routes.py            # /api/chat, /api/chat/stream, /api/health
├── web/                     # Next.js 16 frontend
│   ├── app/                 # App Router pages
│   ├── components/chat/     # ChatInterface, MessageBubble, ExampleCards
│   └── types/chat.ts        # Shared TypeScript types
├── data/
│   └── chroma_db/           # Baked vector database (stateless Cloud Run)
├── config.py                # Single source of configuration
├── pyproject.toml           # Python dependencies (UV)
├── Dockerfile               # Backend container (FastAPI)
├── Dockerfile.web           # Frontend container (Next.js standalone)
└── deploy.md                # Cloud Run deployment guide
```

---

## Getting Started

### Prerequisites

- Python 3.12+ and [UV](https://docs.astral.sh/uv/)
- Node.js 20+
- [Gemini API key](https://aistudio.google.com/)

### Run locally

```bash
git clone https://github.com/mdaniliauskas/resolve-ai.git
cd resolve-ai

# Backend
cp .env.example .env        # add your GOOGLE_API_KEY
uv sync
uv run uvicorn api.main:app --reload
# → http://localhost:8000/docs

# Frontend (separate terminal)
cd web
npm install
npm run dev
# → http://localhost:3000
```

### Run tests

```bash
uv run pytest -v
```

---

## Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](./projetos/resolve-ai/ARCHITECTURE.md) | Detailed architecture with Mermaid diagrams |
| [TECH_DECISIONS.md](./projetos/resolve-ai/TECH_DECISIONS.md) | Architecture Decision Records (ADR-001 to ADR-014) |
| [ROADMAP.md](./projetos/resolve-ai/ROADMAP.md) | 4-phase roadmap (A/B/C/D) with sprint criteria |
| [DEVELOPMENT_GUIDE.md](./projetos/resolve-ai/DEVELOPMENT_GUIDE.md) | Dev philosophy, code patterns |
| [deploy.md](./deploy.md) | Cloud Run deployment step-by-step |

---

## Project Status

**Current phase:** Fase A — Sprint A2 complete ✅ · Fase B next

| Phase | Sprint | Status | Description |
|---|---|:---:|---|
| **Fase A** | A1 | ✅ Done | Next.js frontend + SSE streaming + visual cards |
| **Fase A** | A2 | ✅ Done | structlog · LangSmith (prod) · tema emerald · Gemini 3.1 Flash |
| **Fase B** | — | 🔲 Planned | RAG quality (re-ranking, eval harness) |
| **Fase C** | — | 🔲 Planned | LGPD + auth + conversation history |
| **Fase D** | — | 🔲 Planned | gov.br integration + audio |

---

## Legal Notice

Based on **Law 8.078/1990** (Código de Defesa do Consumidor) and SNDC regulations.

> ⚠️ Resolve Aí provides informational guidance and **does not replace professional legal counsel**.

---

*Resolve Aí — Seu direito, do jeito mais fácil.* 🇧🇷
