# Decisões Técnicas (ADRs) — Resolve Aí 📋

> Architecture Decision Records simplificados. Cada decisão documenta o contexto, a escolha feita, as alternativas consideradas e as consequências.

---

## ADR-001: LLM — Gemini 1.5 Flash

### Contexto
Precisamos de um LLM para os agentes (análise jurídica, estratégia, resposta). As opções principais são: GPT-4o (OpenAI), Claude 3.5 (Anthropic), Gemini 1.5 (Google), ou modelos open-source via Ollama.

### Decisão
**Gemini 1.5 Flash** como LLM principal, com **Ollama (llama3.2)** para desenvolvimento local.

### Justificativa
- ✅ Créditos Google Cloud disponíveis (custo zero para dev/staging)
- ✅ Gemini Flash é otimizado para throughput (rápido e barato)
- ✅ Integração nativa com Vertex AI (deploy facilitado)
- ✅ Suporte a português excelente
- ✅ Demonstra domínio do ecossistema Google (diferencial para portfólio)
- ✅ Ollama para dev local = zero custo no dia a dia

### Alternativas rejeitadas
| Alternativa | Motivo da rejeição |
|------------|-------------------|
| GPT-4o | Sem créditos, custo alto para MVP |
| Claude 3.5 | Sem créditos, embora seja muito bom para texto jurídico |
| Ollama-only | Qualidade inferior para análise jurídica em português |

### Consequências
- Código deve ter abstração para trocar o LLM provider (`LLM_PROVIDER=gemini|ollama`)
- Testes de qualidade devem rodar com Gemini (não Ollama)
- Lock-in mínimo se usar LangChain/LangGraph como abstração

### Status: ✅ Aprovado

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

## ADR-003: Vector Store — ChromaDB (dev) + Vertex AI Vector Search (prod)

### Contexto
Precisamos de um vector store para armazenar embeddings do CDC. Opções: ChromaDB, Pinecone, Weaviate, Qdrant, FAISS, Vertex AI Vector Search.

### Decisão
**ChromaDB** para desenvolvimento local, **Vertex AI Vector Search** para produção.

### Justificativa
- ✅ ChromaDB: simples, roda in-process, sem setup, perfeito para dev
- ✅ Vertex AI Vector Search: managed, escalável, integrado com GCP
- ✅ Separação dev/prod demonstra maturidade de engenharia
- ✅ A abstração no código é simples (interface comum)

### Alternativas rejeitadas
| Alternativa | Motivo da rejeição |
|------------|-------------------|
| Pinecone | SaaS, custo mensal, sem integração GCP nativa |
| FAISS | Sem persistência nativa, mais baixo nível |
| Qdrant | Bom, mas mais complexo de operar que ChromaDB para dev |

### Consequências
- Criar uma interface `VectorStore` com duas implementações
- Testar tanto com ChromaDB quanto com Vertex AI antes do deploy
- ChromaDB grava em disco (diretório `data/chroma_db/`)

### Status: ✅ Aprovado

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

## ADR-006: Frontend — Next.js

### Contexto
Precisamos de um frontend para o chat. Opções: Next.js, Vite + React, Streamlit, Gradio.

### Decisão
**Next.js** para o frontend de produção. **Gradio/Streamlit** como opção para protótipo rápido.

### Justificativa
- ✅ Next.js é production-ready e SEO-friendly
- ✅ App Router (React Server Components) — moderno
- ✅ Deploy fácil no Vercel ou como container
- ✅ Demonstra habilidade full-stack no portfólio

### Observação para o MVP
Para o MVP, considere usar **Gradio** primeiro para validar o backend:

```python
import gradio as gr

def chat(message, history):
    response = requests.post("http://localhost:8000/api/chat", json={"message": message})
    return response.json()["response"]

demo = gr.ChatInterface(fn=chat, title="Resolve Aí")
demo.launch()
```

> 💡 **Dica de Sênior:** Gradio em 5 linhas vs. Next.js em dias. Use Gradio para validar o backend, depois migre para Next.js quando o backend estiver estável.

### Status: ✅ Aprovado (Gradio para protótipo, Next.js para produção)

---

## ADR-007: Embedding Model

### Contexto
Precisamos de um modelo de embedding para o pipeline RAG.

### Decisão
- **Dev local:** `all-MiniLM-L6-v2` (HuggingFace, gratuito, 384d)
- **Produção:** `text-embedding-004` (Gemini, 768d)

### Justificativa
- ✅ MiniLM é leve e funciona offline — perfeito para dev
- ✅ text-embedding-004 tem melhor qualidade para português
- ✅ A troca é configurável via variável de ambiente

### Consequência
- ⚠️ Embeddings não são compatíveis entre modelos. Ao trocar de MiniLM para Gemini, precisa re-indexar TODA a base
- Solução: script de ingestão que re-indexa sob demanda

### Status: ✅ Aprovado

---

## Decisões em Aberto

| ID | Decisão | Status | Prazo |
|----|---------|:------:|:-----:|
| ADR-008 | Estratégia de re-ranking (cross-encoder vs. RRF) | 🟡 Em avaliação | Fase 2 |
| ADR-009 | Persistência de conversas (SQLite vs. PostgreSQL) | 🟡 Em avaliação | Fase 2 |
| ADR-010 | CI/CD (GitHub Actions vs. Cloud Build) | 🔲 Não iniciado | Fase 2 |
| ADR-011 | Monitoramento em produção (LangSmith vs. W&B) | 🔲 Não iniciado | Fase 2 |

---

*Atualize este documento sempre que tomar uma decisão técnica relevante.*
