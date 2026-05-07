<div align="center">

# Resolve Aí 🛡️

[![Português](https://img.shields.io/badge/Português-🇧🇷-009c3b?style=for-the-badge)](#pt-br)
[![English](https://img.shields.io/badge/English-🇺🇸-blue?style=for-the-badge)](#en)

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Acessar-009c3b?style=for-the-badge)](https://resolve-ai-web-444080754389.southamerica-east1.run.app)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mdaniliauskas/resolve-ai)

</div>

---

<a id="pt-br"></a>

<div align="center">

## 🇧🇷 Português

**Seu assistente inteligente para dúvidas sobre o Código de Defesa do Consumidor**

*Multi-agent chatbot que ajuda consumidores brasileiros a entender seus direitos e resolver problemas de consumo com orientação empática e acessível.*

</div>

---

### 🎯 O Problema

Consumidores brasileiros frequentemente **não sabem se o seu problema é coberto pelo CDC**, por onde começar uma reclamação, qual canal tem mais chance de resolução ou quando escalar. O resultado: tempo perdido, frustração e direitos não exercidos.

### 💡 A Solução

O **Resolve Aí** é um chatbot inteligente com pipeline **multi-agente + RAG** que:

1. **Analisa** se o caso se enquadra no CDC e identifica os artigos aplicáveis
2. **Classifica** o tipo de problema (vício de produto, cobrança indevida, propaganda enganosa, etc.)
3. **Planeja** uma estratégia de resolução com canais concretos e passos práticos
4. **Responde** em linguagem empática e acessível — sem juridiquês

### 🏗️ Arquitetura

```
Usuário → Next.js 16 (Cloud Run)
               │  SSE streaming
               ▼
         FastAPI REST API (Cloud Run)
               │
               ▼
      Agente Orquestrador ──→ classifica intenção
         │           │
         ▼           ▼
    RAG (CDC)   Agente Jurídico ──→ identifica artigos CDC
         │           │
         └─────┬─────┘
               ▼
        Agente Estratégia ──→ monta plano de ação
               │
               ▼
        Agente Resposta ──→ formata resposta final (streaming SSE)
```

### 🛠️ Tech Stack

#### 🤖 IA & Agentes
<div align="left">

![Gemini](https://img.shields.io/badge/Gemini_3.1_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![LangSmith](https://img.shields.io/badge/LangSmith-F5A623?style=for-the-badge&logo=langchain&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-6C3483?style=for-the-badge&logoColor=white)

</div>

#### ⚙️ Backend
<div align="left">

![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![UV](https://img.shields.io/badge/UV-DE5FE9?style=for-the-badge&logo=astral&logoColor=white)
![structlog](https://img.shields.io/badge/structlog-2C3E50?style=for-the-badge&logoColor=white)

</div>

#### 🖥️ Frontend
<div align="left">

![Next.js](https://img.shields.io/badge/Next.js_16-000000?style=for-the-badge&logo=next.js&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS_4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![shadcn/ui](https://img.shields.io/badge/shadcn/ui-000000?style=for-the-badge&logo=shadcnui&logoColor=white)

</div>

#### ☁️ Cloud & DevOps
<div align="left">

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Cloud Run](https://img.shields.io/badge/Google_Cloud_Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)

</div>

### 🚀 Como rodar localmente

```bash
git clone https://github.com/mdaniliauskas/resolve-ai.git
cd resolve-ai

# Backend
cp .env.example .env   # adicione sua GOOGLE_API_KEY
uv sync
uv run uvicorn api.main:app --reload
# → http://localhost:8000/docs

# Frontend (outro terminal)
cd web && npm install && npm run dev
# → http://localhost:3000
```

### 📊 Status do Projeto

**Fase atual:** Fase A completa ✅ · Fase B em planejamento

| Fase | Sprint | Status | Descrição |
|------|--------|:------:|-----------|
| **Fase A** | A1 | ✅ | Frontend Next.js + SSE streaming + visual cards |
| **Fase A** | A2 | ✅ | structlog · LangSmith (prod) · tema · Gemini 3.1 Flash |
| **Fase B** | — | 🔲 | Qualidade RAG (re-ranking, eval harness) |
| **Fase C** | — | 🔲 | LGPD + auth + histórico de conversas |
| **Fase D** | — | 🔲 | Integração gov.br + áudio |

### 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [ARCHITECTURE.md](./projetos/resolve-ai/ARCHITECTURE.md) | Arquitetura detalhada com diagramas Mermaid |
| [TECH_DECISIONS.md](./projetos/resolve-ai/TECH_DECISIONS.md) | Architecture Decision Records (ADR-001 a ADR-014) |
| [ROADMAP.md](./projetos/resolve-ai/ROADMAP.md) | Roadmap 4 fases (A/B/C/D) com critérios de sprint |
| [deploy.md](./deploy.md) | Guia de deploy no Cloud Run passo a passo |

> ⚠️ O Resolve Aí oferece orientação informativa e **não substitui assessoria jurídica profissional**.

---

<a id="en"></a>

<div align="center">

## 🇺🇸 English

**Your intelligent assistant for Brazilian consumer rights (CDC)**

*Multi-agent chatbot that helps Brazilian consumers understand their rights and resolve issues with empathetic, accessible guidance.*

[🔝 Back to top / Voltar ao topo](#pt-br)

</div>

---

### 🎯 The Problem

Brazilian consumers frequently **don't know whether their issue is covered by the CDC** (Consumer Protection Code), where to start a complaint, which channel has the best chance of resolution, or when to escalate. The result: lost time, frustration, and unexercised rights.

### 💡 The Solution

**Resolve Aí** is an intelligent chatbot with a **multi-agent + RAG pipeline** that:

1. **Analyzes** whether the case falls under the CDC and identifies applicable articles
2. **Classifies** the problem type (product defect, improper billing, false advertising, etc.)
3. **Plans** a personalized resolution strategy with concrete channels and steps
4. **Responds** in empathetic, accessible language — no legal jargon

### 🏗️ Architecture

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

### 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Gemini 3.1 Flash (Google GenAI SDK) |
| **Agent Orchestration** | LangGraph |
| **Observability** | LangSmith |
| **RAG / Embeddings** | ChromaDB + `gemini-embedding-001` |
| **Backend** | Python 3.12 + FastAPI + UV |
| **Logging** | structlog (JSON in prod / console in dev) |
| **Frontend** | Next.js 16 + Tailwind CSS 4 + shadcn/ui |
| **Streaming** | Server-Sent Events (SSE) |
| **Deploy** | Docker + Google Cloud Run (`southamerica-east1`) |

### 🚀 Getting Started

```bash
git clone https://github.com/mdaniliauskas/resolve-ai.git
cd resolve-ai

# Backend
cp .env.example .env   # add your GOOGLE_API_KEY
uv sync
uv run uvicorn api.main:app --reload
# → http://localhost:8000/docs

# Frontend (separate terminal)
cd web && npm install && npm run dev
# → http://localhost:3000
```

### 📊 Project Status

**Current phase:** Phase A complete ✅ · Phase B next

| Phase | Sprint | Status | Description |
|-------|--------|:------:|-------------|
| **Phase A** | A1 | ✅ | Next.js frontend + SSE streaming + visual cards |
| **Phase A** | A2 | ✅ | structlog · LangSmith (prod) · theme · Gemini 3.1 Flash |
| **Phase B** | — | 🔲 | RAG quality (re-ranking, eval harness) |
| **Phase C** | — | 🔲 | LGPD + auth + conversation history |
| **Phase D** | — | 🔲 | gov.br integration + audio |

> ⚠️ Resolve Aí provides informational guidance and **does not replace professional legal counsel**.

---

<div align="center">

*Resolve Aí — Seu direito, do jeito mais fácil. 🇧🇷*

[![LinkedIn](https://img.shields.io/badge/-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mdaniliauskas)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mdaniliauskas)

</div>
