# Roadmap — Resolve Aí 🗺️

> Roadmap detalhado com 3 fases, milestones, critérios de aceite e estimativas.

---

## Visão Geral

```
Fase 1: MVP ─────────── Chat + RAG CDC + Análise + Encaminhamento
Fase 2: Enriquecimento ─ Jurisprudência + Estratégia + Histórico + PDF
Fase 3: Escala ────────── Integrações + Cartas + Painel + Mobile
```

---

## Fase 1 — MVP (4-6 semanas)

> **Objetivo:** Chat funcional que analisa situações de consumo à luz do CDC e orienta o consumidor.

### Sprint 1: Fundação (Semana 1-2)

| Tarefa | Componente | Critério de Aceite | Estimativa |
|--------|:----------:|-------------------|:----------:|
| Setup do projeto (repo, venv, CI básico) | Infra | Repo no GitHub + README | 2h |
| API esqueleto (FastAPI + health check) | Backend | `/api/health` retorna 200 | 2h |
| Download e limpeza do CDC | Data | `cdc_clean.txt` gerado | 3h |
| Pipeline de chunking com metadata | RAG | Chunks indexados no ChromaDB | 4h |
| Retrieval básico (similarity search) | RAG | Query retorna chunks relevantes | 3h |
| Teste do retrieval com golden set | RAG | ≥ 70% dos artigos corretos no top-5 | 3h |

**Entregável:** `POST /api/search?q=...` que retorna chunks do CDC relevantes.

### Sprint 2: Inteligência (Semana 3-4)

| Tarefa | Componente | Critério de Aceite | Estimativa |
|--------|:----------:|-------------------|:----------:|
| Agente de Análise Jurídica | Agents | Identifica artigos em 8/10 golden tests | 6h |
| Agente Orquestrador | Agents | Roteia corretamente CDC vs. fora do CDC | 4h |
| Agente de Resposta | Agents | Resposta clara e acionável | 4h |
| Integração LangGraph | Agents | Grafo end-to-end funcionando | 4h |
| Endpoint `/api/chat` completo | Backend | Resposta com análise + fontes | 3h |
| Testes unitários dos agentes | Tests | ≥ 10 testes passando | 4h |

**Entregável:** API funcional que recebe mensagem e retorna análise completa.

### Sprint 3: Interface + Polish (Semana 5-6)

| Tarefa | Componente | Critério de Aceite | Estimativa |
|--------|:----------:|-------------------|:----------:|
| Frontend chat (Gradio ou Next.js mínimo) | Frontend | Interface funcional | 6h |
| Agente de Estratégia | Agents | Sugere canais priorizados | 4h |
| Disclaimer legal na UI | Frontend | Visível antes de usar | 1h |
| Dockerização completa | Infra | `docker compose up` funciona | 3h |
| Avaliação com golden test set completo | Quality | ≥ 80% precisão | 3h |
| README final com demo | Docs | Screenshots + instruções | 3h |

**Entregável:** MVP demonstrável — chat web que orienta consumidores.

### 🏁 Milestone: MVP Completo

**Critérios de aceite do MVP:**
- [ ] Chat funciona end-to-end (pergunta → resposta com artigos)
- [ ] Precisão ≥ 80% no golden test set (10 cenários)
- [ ] Latência < 15s por request
- [ ] Casos fora do CDC são tratados adequadamente
- [ ] Disclaimer legal presente
- [ ] README com instruções de setup e demo
- [ ] Deploy funcional (local ou Cloud Run)

---

## Fase 2 — Enriquecimento (4-6 semanas)

> **Objetivo:** Melhorar a qualidade das respostas, adicionar funcionalidades de retenção e valor.

### Sprint 4: RAG Avançado

| Tarefa | Componente | Critério de Aceite |
|--------|:----------:|--------------------|
| Adicionar jurisprudência ao RAG (STJ) | RAG | ≥ 20 decisões relevantes indexadas |
| Re-ranking de resultados | RAG | Melhoria no Context Precision (RAGAS) |
| Notebook de avaliação comparativa | Evaluation | CDC puro vs. CDC + Jurisprudência medido |
| Avaliação RAGAS completa | Evaluation | 4 métricas medidas e documentadas |

### Sprint 5: Funcionalidades

| Tarefa | Componente | Critério de Aceite |
|--------|:----------:|--------------------|
| Histórico de conversas (sessão) | Backend | Usuário mantém contexto na sessão |
| Exportação do caso em PDF | Backend | PDF gerado com análise + passos |
| Agente de Estratégia avançado | Agents | Priorização por tipo de empresa e gravidade |
| Observabilidade (LangSmith ou logging) | Infra | Traces de cada request visíveis |

### Sprint 6: Deploy e Produção

| Tarefa | Componente | Critério de Aceite |
|--------|:----------:|--------------------|
| Deploy no Google Cloud Run | Infra | App rodando em URL pública |
| Gemini como LLM principal via Vertex AI | LLM | Migração de Ollama → Gemini sem regressão |
| Vertex AI Vector Search | RAG | Migração de ChromaDB → Vertex AI |
| CI/CD (GitHub Actions) | Infra | Push → Test → Deploy automático |

### 🏁 Milestone: Produto Polido

- [ ] Respostas embasadas em CDC + Jurisprudência
- [ ] Avaliação RAGAS documentada como mini-pesquisa
- [ ] Deploy em produção (Cloud Run)
- [ ] PDF exportável
- [ ] Histórico de conversas funcional

---

## Fase 3 — Escala (6-8 semanas)

> **Objetivo:** Escalar funcionalidades e alcance.

### Features Planejadas

| Tarefa | Componente | Impacto |
|--------|:----------:|---------|
| Integração com consumidor.gov.br (API) | Integração | Preenchimento automático de reclamação |
| Geração de cartas/e-mails de reclamação | Agents | Modelo de carta com dados do caso |
| Painel de acompanhamento de casos | Frontend | Dashboard com status das reclamações |
| App mobile (React Native / PWA) | Frontend | Acesso via celular |
| Autenticação de usuários | Backend | Persistência de dados por usuário |
| Analytics de uso | Infra | Métricas de engajamento |

### 🏁 Milestone: Produto Escalável

- [ ] Pelo menos 2 integrações externas
- [ ] Base de usuários ativos
- [ ] Métricas de satisfação coletadas

---

## Cronograma Alinhado com Preparação GenAI

> Sincronizado com o curso Ed Donner e o plano de preparação para a vaga.

```
Semana 1-2  │ Sprint 1     │ Curso: Setup + Chatbot     │ RAG do CDC pronto
Semana 3-4  │ Sprint 2     │ Curso: RAG + Embeddings    │ Agentes funcionais
Semana 5-6  │ Sprint 3     │ Curso: Advanced RAG        │ MVP completo ✨
Semana 7-8  │ Sprint 4     │ Curso: Fine-tuning         │ RAGAS avaliação
Semana 9-10 │ Sprint 5-6   │ Capstone + Prep entrevista │ Deploy Cloud Run
```

> 💡 **Dica de Sênior:** Esse cronograma é agressivo. Se atrasar, priorize: **MVP funcional > avaliação > polimento**. Um MVP que funciona vale mais que um projeto half-done com features avançadas.

---

## Priorização (MoSCoW)

| Prioridade | Feature |
|:----------:|---------|
| **Must** | Chat + RAG CDC + Análise jurídica + Encaminhamento |
| **Should** | Avaliação RAGAS + Deploy Cloud Run + Testes |
| **Could** | Jurisprudência + PDF + Histórico |
| **Won't (agora)** | Mobile + Auth + Integrações externas |

---

*Atualize este roadmap conforme o progresso. Marque com ✅ os itens concluídos.*
