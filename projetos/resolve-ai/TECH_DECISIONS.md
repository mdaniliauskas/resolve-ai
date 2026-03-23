# Decisões Técnicas (ADRs) — Resolve Aí 📋

> Architecture Decision Records simplificados. Cada decisão documenta o contexto, a escolha feita, as alternativas consideradas e as consequências.

---

## ADR-001: LLM — Gemini 3.1 Flash Lite

### Contexto
Precisamos de um LLM para os agentes (análise jurídica, estratégia, resposta). As opções principais são: GPT-4o (OpenAI), Claude 3.5 (Anthropic), Gemini (Google), ou modelos open-source via Ollama.

### Decisão
**Gemini 3.1 Flash Lite** como LLM principal via SDK `google-genai`, com **Ollama (llama3.2)** como fallback para desenvolvimento local offline.

### Evolução
- Inicialmente planejado Gemini 1.5 Flash via Vertex AI.
- Migrado para **Gemini 3.1 Flash Lite** via SDK `google-genai` (mais direto, sem overhead do Vertex AI para o MVP).
- O wrapper `llm_client.py` abstrai o provider, permitindo troca via `LLM_PROVIDER=gemini|ollama`.

### Justificativa
- ✅ Créditos Google Cloud disponíveis (custo zero para dev/staging)
- ✅ Flash Lite otimizado para throughput (rápido e barato)
- ✅ SDK `google-genai` mais simples que Vertex AI para o contexto do MVP
- ✅ Suporte a português excelente
- ✅ Ollama para dev local = zero custo no dia a dia

### Alternativas rejeitadas
| Alternativa | Motivo da rejeição |
|------------|-------------------|
| GPT-4o | Sem créditos, custo alto para MVP |
| Claude 3.5 | Sem créditos, embora seja muito bom para texto jurídico |
| Ollama-only | Qualidade inferior para análise jurídica em português |
| Vertex AI SDK | Overhead de setup desnecessário para o MVP |

### Consequências
- Código tem abstração para trocar provider (`LLM_PROVIDER=gemini|ollama` em `config.py`)
- Testes de qualidade devem rodar com Gemini (não Ollama)
- Lock-in mínimo via wrapper `llm_client.py`

### Status: ✅ Aprovado e implementado

---

## ADR-002: Framework de Agentes — LangGraph

### Contexto
Precisamos de um framework para orquestrar os 4 agentes. Opções: LangGraph, CrewAI, AutoGen, ou implementação custom.

### Decisão
**LangGraph** (by LangChain).

### Justificativa
- ✅ Grafo de estados explícito (StateGraph) — fácil de entender e debugar
- ✅ Determinístico — fluxo previsível, sem "agentes decidindo sozinhos"
- ✅ Ecossistema LangChain — integração com LLMs, tools, retrievers
- ✅ Boa documentação e comunidade ativa
- ✅ Suporta streaming, checkpointing e human-in-the-loop (útil para fases futuras)
- ✅ Requisito relevante para portfólio (vaga pede experiência com agents)

### Alternativas rejeitadas
| Alternativa | Motivo da rejeição |
|------------|-------------------|
| CrewAI | Mais opinado, menos controle sobre o fluxo |
| AutoGen (Microsoft) | Foco em multi-agent conversation, overengineering para o MVP |
| Custom | Reinventar a roda, menos valor de portfólio |

### Consequências
- Dependência do ecossistema LangChain (que muda rápido)
- Curva de aprendizado moderada (conceito de StateGraph)
- Facilita adicionar novos agentes no futuro

### Status: ✅ Aprovado

---

## ADR-003: Vector Store — ChromaDB (dev e produção)

### Contexto
Precisamos de um vector store para armazenar embeddings do CDC e jurisprudências do STJ. Opções: ChromaDB, Pinecone, Weaviate, Qdrant, FAISS, Vertex AI Vector Search.

### Decisão
**ChromaDB** para desenvolvimento local e produção (baked na imagem Docker).

### Evolução
- Inicialmente planejado ChromaDB (dev) + Vertex AI Vector Search (prod).
- Vertex AI Vector Search desconsiderado: overengineering para o volume de dados do MVP (~50 chunks CDC + ~30 STJ).
- ChromaDB com persistência em disco atende perfeitamente. O banco vetorial é empacotado na imagem Docker para deploy.

### Justificativa
- ✅ ChromaDB: simples, roda in-process, sem setup
- ✅ Persistência em disco (`data/chroma_db/`) é suficiente para o volume atual
- ✅ Baked na imagem Docker = zero dependência externa em produção
- ✅ Configurado com `hnsw:space: cosine` para distance metric

### Alternativas rejeitadas
| Alternativa | Motivo da rejeição |
|------------|-------------------|
| Vertex AI Vector Search | Overengineering para ~80 chunks |
| Pinecone | SaaS, custo mensal, dependência externa |
| FAISS | Sem persistência nativa, mais baixo nível |
| Qdrant | Mais complexo de operar que ChromaDB |

### Consequências
- Simplicidade máxima: sem serviço externo de banco vetorial
- Se escalar para milhares de documentos, reavaliar Vertex AI Vector Search
- ChromaDB grava em disco (diretório `data/chroma_db/`)

### Status: ✅ Aprovado e implementado

---

## ADR-004: Estratégia de Chunking do CDC

### Contexto
O CDC (Lei 8.078/1990) tem 119 artigos organizados em Títulos, Capítulos e Seções. A estratégia de chunking impacta diretamente a qualidade do RAG.

### Decisão
**Recursive Character Text Splitter** com metadata hierárquica.

### Configuração
| Parâmetro | Valor |
|-----------|:-----:|
| Chunk Size | 800 tokens |
| Overlap | 200 tokens |
| Separators | `["\n\n", "\n", "Art.", ". "]` |
| Metadata | `{titulo, capitulo, secao, artigo, numero_artigo}` |

### Justificativa
- ✅ O CDC tem parágrafos curtos — 800 tokens captura 2-3 artigos com contexto
- ✅ Overlap de 200 preserva artigos que cairiam na borda
- ✅ Separador "Art." respeita a estrutura natural do CDC
- ✅ Metadata hierárquica permite filtragem por seção

### Alternativas consideradas
| Alternativa | Trade-off |
|------------|-----------|
| Semantic chunking | Melhor qualidade, mais complexo, mais lento |
| 1 chunk por artigo | Chunks muito pequenos, perdem contexto |
| Chunks de 1500+ tokens | Diluem a relevância, aumentam custo |

### Status: ✅ Aprovado (revisitar após avaliação RAGAS)

---

## ADR-005: Backend Framework — FastAPI

### Contexto
Precisamos de um framework web Python para a API REST.

### Decisão
**FastAPI**.

### Justificativa
- ✅ Async nativo — essencial para chamadas LLM (I/O bound)
- ✅ Pydantic integrado — validação automática de request/response
- ✅ OpenAPI/Swagger automático — documentação grátis
- ✅ Performance excelente (baseado em Starlette)
- ✅ Padrão de mercado para APIs Python modernas

### Alternativas rejeitadas
| Alternativa | Motivo |
|------------|--------|
| Flask | Sync por padrão, menos moderno |
| Django REST | Overengineering para API simples |
| Litestar | Menor ecossistema |

### Status: ✅ Aprovado

---

## ADR-006: Frontend — Gradio 6

### Contexto
Precisamos de um frontend para o chat. Opções: Next.js, Vite + React, Streamlit, Gradio.

### Decisão
**Gradio 6** como frontend de produção.

### Evolução
- Inicialmente planejado Gradio (protótipo) → Next.js (produção).
- Na prática, Gradio 6 atendeu plenamente: chat interface, disclaimer legal, autenticação nativa, e deploy direto no Cloud Run.
- Next.js desconsiderado: overhead de desenvolvimento desproporcional para a fase atual do projeto.

### Justificativa
- ✅ Gradio 6 é production-ready com auth nativo e temas customizáveis
- ✅ Integração direta com o backend Python (sem camada HTTP separada)
- ✅ Deploy simples: mesmo container, mesma porta
- ✅ Autenticação built-in (auth: `visitante/resolveai`)
- ✅ Permitiu foco total no backend e na qualidade do RAG

### Alternativas descartadas
| Alternativa | Motivo |
|------------|--------|
| Next.js | Overhead de dev, camada desnecessária para MVP |
| Streamlit | Menos flexível que Gradio para chat interfaces |
| Vite + React | Mesmo problema do Next.js |

### Status: ✅ Aprovado e implementado

---

## ADR-007: Embedding Model — gemini-embedding-001

### Contexto
Precisamos de um modelo de embedding para o pipeline RAG.

### Decisão
**`gemini-embedding-001`** via SDK `google-genai` para dev e produção.

### Evolução
- Inicialmente planejado MiniLM (dev) + text-embedding-004 (prod).
- Migrado diretamente para `gemini-embedding-001` (unificando dev/prod).
- Implementado como `GeminiEmbeddingFunction` customizada em `rag/embedder.py`, compatível com ChromaDB.
- Configurado com `task_type: RETRIEVAL_DOCUMENT` para otimizar retrieval.

### Justificativa
- ✅ Melhor qualidade semântica para português jurídico vs. MiniLM
- ✅ Unificar dev/prod elimina bugs de incompatibilidade de embeddings
- ✅ Resultou em **90% de precisão** no Golden Test Set (melhoria significativa)
- ✅ ChromaDB embedding function customizada (`rag/embedder.py`) encapsula a API

### Alternativas descartadas
| Alternativa | Motivo |
|------------|--------|
| all-MiniLM-L6-v2 | Qualidade inferior para português jurídico |
| text-embedding-004 | Substituído pelo mais recente gemini-embedding-001 |
| Modelos HuggingFace multilíngues | Complexidade desnecessária com API do Gemini disponível |

### Consequência
- Depende de API key do Google para qualquer ambiente (inclusive dev)
- Script `rag/ingest.py` re-indexa sob demanda quando necessário

### Status: ✅ Aprovado e implementado

---

## Decisões em Aberto

| ID | Decisão | Status | Prazo |
|----|---------|:------:|:-----:|
| ADR-008 | Estratégia de re-ranking (cross-encoder vs. RRF) | 🟡 Em avaliação | Fase 3 |
| ADR-009 | Persistência de conversas (SQLite vs. PostgreSQL) | 🟡 Em avaliação | Fase 3 |
| ADR-010 | CI/CD (GitHub Actions vs. Cloud Build) | 🔲 Não iniciado | Fase 3 |
| ADR-011 | Monitoramento em produção (LangSmith vs. W&B) | 🔲 Não iniciado | Fase 3 |

---

*Atualize este documento sempre que tomar uma decisão técnica relevante.*
