# Resolve Aí 🛡️

> Seu assistente inteligente para dúvidas sobre o Código de Defesa do Consumidor

Um chatbot multi-agente que ajuda consumidores brasileiros a entender seus direitos sob o *Código de Defesa do Consumidor* (CDC / Lei 8.078/1990) e obter orientação concreta sobre como resolver seus problemas.

---

## 🎯 O Problema

Consumidores brasileiros frequentemente **não sabem se seu problema é amparado pelo CDC**, por onde começar a reclamar, qual canal tem mais chance de resolução rápida, ou quando escalar para instâncias formais. O resultado: tempo perdido, frustração e direitos não exercidos.

## 💡 A Solução

O **Resolve Aí** é um chatbot inteligente com arquitetura **multi-agentes + RAG** que:

1. **Analisa** se o caso se enquadra no CDC e identifica artigos aplicáveis
2. **Classifica** o tipo de problema (defeito, cobrança indevida, propaganda enganosa, etc.)
3. **Planeja** uma estratégia personalizada de resolução
4. **Orienta** com passos concretos e links para os canais mais adequados

---

## 🧠 Arquitetura

```
Usuário → Interface Chat (Gradio)
                │
                ▼
         FastAPI REST API
                │
                ▼
      Agente Orquestrador ──→ classifica intenção
          │           │
          ▼           ▼
     RAG (CDC)   Ag. Análise Jurídica ──→ identifica artigos do CDC
          │           │
          └─────┬─────┘
                ▼
        Ag. Estratégia ──→ monta plano de ação
                │
                ▼
        Ag. Resposta ──→ formata resposta final
```

> 📐 Arquitetura completa com diagramas Mermaid em [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## ⚙️ Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| **LLM** | Gemini 3.1 Flash Lite (Google GenAI SDK `google-genai`) |
| **Orquestração de Agentes** | LangGraph |
| **RAG / Embeddings** | ChromaDB + `gemini-embedding-001` (Cosine Distance) |
| **Backend** | Python 3.12 + FastAPI |
| **Frontend** | Gradio 6 |
| **Gerenciador de Pacotes** | UV |
| **Deploy** | Docker + Google Cloud Run (com Safeguards) |

---

## 📁 Estrutura do Projeto

```
resolve-ai/
├── agents/                  # Agentes de IA (LangGraph nodes)
│   ├── llm_client.py        # Wrapper centralizado do Gemini SDK
│   ├── orchestrator.py      # Classificação de intenção e roteamento
│   ├── legal_analysis.py    # Identificação de artigos do CDC via RAG
│   ├── strategy.py          # Planejamento de canais de resolução
│   ├── response.py          # Formatação da resposta final
│   └── workflow.py          # Orquestração do StateGraph (LangGraph)
├── rag/                     # Pipeline RAG
│   ├── ingest.py            # Ingestão de documentos (download → chunk → embed → index)
│   ├── embedder.py          # Embedding function customizada (Gemini)
│   └── retrieval.py         # Busca por similaridade + filtragem por threshold
├── api/                     # Backend FastAPI
│   ├── main.py              # Entry point do app + middleware
│   └── routes.py            # Endpoints /api/chat, /api/health
├── frontend/                # Interface chat Gradio
│   └── app.py               # Chat UI com disclaimer legal
├── data/
│   ├── cdc/                 # Documentos-fonte do CDC
│   └── jurisprudencia/      # Súmulas e temas do STJ
├── evaluation/              # Golden test set (10 cenários CDC) + RAGAS
├── tests/                   # Testes unitários + integração (32 testes)
├── config.py                # Fonte única de configuração (lê do .env)
├── pyproject.toml           # Dependências (gerenciadas com UV)
├── Dockerfile               # Imagem de container para produção
├── deploy.md                # Instruções e safeguards do deploy Cloud Run
└── .env.example             # Template de variáveis de ambiente
```

---

## 🚀 Como Começar

### Pré-requisitos

- Python 3.12+
- [UV](https://docs.astral.sh/uv/) (gerenciador de pacotes)
- [Chave da API Gemini](https://aistudio.google.com/) **ou** [Ollama](https://ollama.com/) para LLM local

### Setup

```bash
# 1. Clone o repositório
git clone https://github.com/mdaniliauskas/resolve-ai.git
cd resolve-ai

# 2. Instale as dependências (UV cria o virtualenv automaticamente)
uv sync

# 3. Configure o ambiente
cp .env.example .env
# Edite .env com sua GOOGLE_API_KEY

# 4. Inicie a interface de chat (Auth: visitante/resolveai)
uv run python frontend/app.py
# → http://localhost:7860

# Ou inicie apenas a API
uv run uvicorn api.main:app --reload
# → http://localhost:8000/docs

# Rodar testes
uv run pytest -v
```

> Guia completo de setup em [SETUP.md](./SETUP.md)

---

## 📊 Status do Projeto

**Fase atual:** Enriched & Deployed (Sprint 6 completo ✅)

| Fase | Status | Descrição |
|---|:---:|---|
| **Sprint 1** | ✅ Done | Scaffold, pipeline RAG, golden test set |
| **Sprint 2** | ✅ Done | Pipeline multi-agente (orquestrador, jurídico, estratégia, resposta) |
| **Sprint 3** | ✅ Done | Chat UI Gradio, disclaimer legal, README |
| **Sprint 4 (RAG)** | ✅ Done | Migração para `gemini-embedding-001` (90% Precision Score) |
| **Sprint 5 (Deploy)** | ✅ Done | Google Cloud Run Deploy + Safeguards (Auth & Token Caps) |
| **Escala** | 🔲 Planejado | Integração gov.br + Cartas automáticas + Mobile |

> 📋 Roadmap detalhado em [ROADMAP.md](./ROADMAP.md)

---

## 📚 Documentação

| Documento | Descrição |
|---|---|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Arquitetura detalhada com diagramas Mermaid |
| [MVP_SPEC.md](./MVP_SPEC.md) | Especificação técnica: API, templates de prompt, critérios de aceite |
| [TECH_DECISIONS.md](./TECH_DECISIONS.md) | Architecture Decision Records (ADRs) |
| [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) | Filosofia de dev, code patterns e dicas de sênior |
| [ROADMAP.md](./ROADMAP.md) | Roadmap com milestones e critérios de aceite |
| [SETUP.md](./SETUP.md) | Guia passo a passo de setup do ambiente |

---

## 📄 Base Legal

Baseado na **Lei nº 8.078/1990** (Código de Defesa do Consumidor) e normas do SNDC.

> ⚠️ O Resolve Aí oferece orientação informativa e **não substitui assessoria jurídica profissional**. Para casos complexos, recomenda-se consultar um advogado.

---

*Resolve Aí — Seu direito, do jeito mais fácil.* 🇧🇷
