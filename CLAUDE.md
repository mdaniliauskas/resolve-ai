# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Resolve Aí** is a multi-agent chatbot that helps Brazilian consumers understand their rights under the CDC (Código de Defesa do Consumidor, Lei 8.078/1990). It combines a LangGraph agent pipeline with RAG over CDC source documents.

## Commands

```bash
# Install dependencies (UV manages the virtualenv automatically)
uv sync

# Run the Gradio frontend (http://localhost:7860, auth: visitante/resolveai)
uv run python frontend/app.py

# Run the FastAPI backend only (http://localhost:8000/docs)
uv run uvicorn api.main:app --reload

# Run all tests
uv run pytest -v

# Run a single test file
uv run pytest tests/test_agents.py -v

# Run golden test set (requires real GOOGLE_API_KEY)
uv run pytest tests/test_golden_set.py -v

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy agents/ api/ config.py
```

Copy `.env.example` to `.env` and set `GOOGLE_API_KEY` before running.

## Architecture

Five-agent LangGraph pipeline triggered by `POST /api/chat`:

```
Gradio UI (frontend/app.py)
  → FastAPI (api/routes.py)
    → LangGraph StateGraph (agents/workflow.py)
        1. orchestrator_node  — classifies intent: consumer_complaint | general_question | greeting | out_of_scope
        2. retrieval_node     — RAG: cosine similarity search (threshold 0.6, top-7 chunks) from ChromaDB
        3. legal_analysis_node — matches CDC articles, classifies severity, extracts rights
        4. strategy_node      — plans resolution channels (SAC → PROCON → Judicial)
        5. response_node      — formats consumer-facing response
```

### Key modules

| Path | Role |
|------|------|
| `agents/llm_client.py` | Singleton for all Gemini calls (google-genai SDK); swap provider via `config.py` |
| `agents/workflow.py` | LangGraph StateGraph wiring all nodes together |
| `rag/retrieval.py` | Similarity search against ChromaDB; threshold and top-k configured in `config.py` |
| `rag/ingest.py` | Chunks CDC documents (3200 chars / 800 overlap) and indexes into ChromaDB |
| `config.py` | BaseSettings loaded from `.env`; all tunable parameters live here |

### Data flow for a consumer complaint

`orchestrator` classifies → `retrieval` fetches relevant CDC chunks → `legal_analysis` produces JSON (case determination, articles, precedents, rights) → `strategy` produces JSON (prioritized channels, tips) → `response` formats the final message.

Out-of-scope or greeting intents short-circuit: they skip retrieval/legal/strategy and go straight to `response`.

## Testing

- Unit tests mock all LLM calls; integration and golden-set tests hit the real API.
- `asyncio_mode = "auto"` is set in `pyproject.toml` — no `@pytest.mark.asyncio` needed.
- The golden test set (`tests/test_golden_set.py`) has 10 real CDC scenarios used for regression.

## Tooling

- **Ruff** enforces `line-length = 100`.
- **MyPy** runs in strict mode; all public functions need type annotations.
- **UV** is the package manager — use `uv add <pkg>` to add dependencies, not `pip`.

## Skills

Project-level behavioral skills live in [`.agent/skills/`](.agent/skills/). They are applied automatically when the context matches — no need to invoke them explicitly.

| Skill | When it applies |
|-------|----------------|
| [`human-friendly-code`](.agent/skills/human-friendly-code/SKILL.md) | Every code generation or review task |
| [`human-commits`](.agent/skills/human-commits/SKILL.md) | Every git commit |
| [`dev-journal`](.agent/skills/dev-journal/SKILL.md) | End of each sprint or when explicitly requested |
| [`check-latest-versions`](.agent/skills/check-latest-versions/SKILL.md) | Any time a library, API, SDK, MCP server, model ID, or Docker image is added, updated, or referenced |

## Deployment

Docker image bakes in ChromaDB + CDC data for stateless Cloud Run deployment. The container exposes port `8080` (set `GRADIO_SERVER_PORT=8080`). See `deploy.md` for the full Cloud Run procedure.
