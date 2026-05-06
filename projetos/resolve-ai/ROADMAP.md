# Roadmap — Resolve Aí 🗺️

> Atualizado: 2026-05-06 | Ritmo: ~10h/semana | Cronograma ajustado conforme avanço real.

---

## Histórico — Fases 1 e 2 (Concluído ✅)

| Sprint | Entregável principal | Status |
|--------|---------------------|:------:|
| Sprint 1 | Setup, RAG CDC, ChromaDB | ✅ |
| Sprint 2 | Agentes LangGraph, `/api/chat` | ✅ |
| Sprint 3 | Frontend Gradio, Agente de Estratégia, Docker | ✅ |
| Sprint 4 | RAG avançado, `gemini-embedding-001`, RAGAS (90% precisão) | ✅ |
| Sprint 5 | Jurisprudência STJ indexada, migração SDK `google-genai` | ✅ |
| Sprint 6 | Deploy Cloud Run, auth Gradio, safeguards de tokens | ✅ |

---

## Nova Estrutura — 4 Fases

```
Fase A: Fundação de Produto ── Frontend Next.js + streaming + observabilidade
Fase B: Engenharia de Qualidade ── Evals em CI + cost engineering + type safety
Fase C: Produto para Usuários Reais ── Auth + persistência + LGPD + PDF
Fase D: Diferenciação ── Áudio + integrações + analytics
```

---

## Fase A — Fundação de Produto (~4 semanas)

> **Objetivo:** Deixar de parecer demo. Virar UX de produto que impressiona Tech Lead e que o usuário-alvo consegue usar.

### Sprint A1 — Novo Frontend (semana 1-2)

| Tarefa | Componente | Critério de aceite |
|--------|:----------:|--------------------|
| Setup Next.js 16 + Tailwind 4 + shadcn/ui | Frontend | `npm run dev` funciona, página inicial renderizando |
| Layout base: header, chat area, footer | Frontend | Estrutura responsiva no mobile e desktop |
| Integração com `/api/chat` via Vercel AI SDK 6 | Frontend | Mensagem enviada, resposta recebida |
| Streaming token-a-token | Frontend | Resposta aparece progressivamente (não espera tudo) |
| Estados de carregamento humanizados | Frontend | "Estou consultando o CDC..." durante processamento |
| Microcopy revisada com tom empático | Frontend | Sem jargão jurídico cru; linguagem de "amigo que entende" |

**Entregável:** Novo frontend rodando localmente, consumindo a API existente.

### Sprint A2 — Cartões e Observabilidade (semana 3-4)

| Tarefa | Componente | Critério de aceite |
|--------|:----------:|--------------------|
| Resposta em cartões visuais | Frontend | "Seus direitos", "Próximo passo", "Artigos CDC" separados |
| Exemplos como cards clicáveis (não lista) | Frontend | 4 cards na tela inicial, clique preenche o campo |
| Logging estruturado com `structlog` | Backend | Cada request logado em JSON com trace_id |
| LangSmith para tracing de agentes | Backend | Traces visíveis no dashboard LangSmith |
| Gradio mantido como `frontend-legacy/` | Infra | Continua funcional em paralelo |
| CORS e deploy do frontend no Cloud Run | Infra | Frontend novo em produção |

**Entregável:** Produto visualmente refinado em produção. Frontend Gradio aposentado.

### 🏁 Milestone Fase A — Produto Fundado

- [ ] Frontend Next.js em produção (URL pública)
- [ ] Streaming funcionando end-to-end
- [ ] Resposta em cartões visuais (sem markdown corrido)
- [ ] Tracing de cada request no LangSmith
- [ ] Logging estruturado em produção

---

## Fase B — Engenharia de Qualidade (~3 semanas)

> **Objetivo:** O que separa "fiz um chatbot" de "operei um sistema de IA". Foco em rigor de engenharia visível pra Tech Lead.

### Sprint B1 — Evals e CI (semana 5-6)

| Tarefa | Componente | Critério de aceite |
|--------|:----------:|--------------------|
| Golden test set em GitHub Actions | CI | PR que quebra ≥1 cenário é bloqueado |
| RAGAS rodando em CI | CI | 4 métricas (faithfulness, answer_relevancy, context_precision, context_recall) medidas por PR |
| Badge de qualidade no README | Docs | Score RAGAS atual visível no repo |
| Testes de integração E2E com mock LLM | Tests | Pipeline completo testado sem custo de API |

### Sprint B2 — Cost Engineering e Type Safety (semana 7)

| Tarefa | Componente | Critério de aceite |
|--------|:----------:|--------------------|
| Rate limiting por IP (middleware FastAPI) | Backend | Max 20 req/hora por IP |
| Prompt caching da Gemini | Backend | Cache hit rate > 60% em sessões longas |
| Cache de embeddings (não re-embedar mesmos chunks) | RAG | Latência de retrieval < 200ms |
| Cliente TypeScript gerado do OpenAPI | Frontend | Tipos do backend em sync com o front automaticamente |

### 🏁 Milestone Fase B — Engenharia Sólida

- [ ] CI bloqueia PRs que degradam qualidade do RAG
- [ ] Custo por request estimado e documentado
- [ ] Type safety end-to-end backend ↔ frontend
- [ ] README com badges: CI ✅, RAGAS score, cobertura de testes

---

## Fase C — Produto para Usuários Reais (~5 semanas)

> **Objetivo:** Infraestrutura mínima para convidar usuários reais sem quebrar nem vazar dados.

### Funcionalidades

| Tarefa | Componente | Critério de aceite |
|--------|:----------:|--------------------|
| Autenticação (magic link via Supabase Auth ou Clerk) | Auth | Login sem senha funcional |
| Persistência de conversas (Supabase Postgres) | Backend | Histórico visível entre sessões |
| Histórico por usuário na UI | Frontend | Sidebar com conversas anteriores |
| Geração de carta de reclamação em PDF | Backend | PDF com análise, direitos e passos gerado por request |
| LGPD: política de privacidade + consentimento + direito ao esquecimento | Legal/Backend | Dados deletáveis, política publicada |
| Soft launch com 20-50 usuários convidados | Produto | Feedback coletado, bugs corrigidos |

### 🏁 Milestone Fase C — Produto com Usuários

- [ ] Usuários conseguem criar conta e recuperar histórico
- [ ] PDF de carta exportável
- [ ] LGPD compliance básico
- [ ] Pelo menos 20 usuários reais tendo usado

---

## Fase D — Diferenciação (~5 semanas)

> **Objetivo:** Funcionalidades que viram conversa e aumentam alcance.

| Tarefa | Componente | Impacto esperado |
|--------|:----------:|-----------------|
| Áudio bidirecional (Web Speech API) | Frontend | Acessibilidade para baixa escolaridade |
| Integração consumidor.gov.br | Backend | Preenche reclamação automaticamente |
| Painel de acompanhamento de casos | Frontend | Retenção de usuário |
| Analytics de uso (PostHog) | Infra | Entender o que o usuário realmente faz |
| Notificações (e-mail) sobre atualizações do caso | Backend | Engajamento ativo |

---

## Priorização MoSCoW Atual

| Prioridade | Feature | Status |
|:----------:|---------|:------:|
| **Must** | Frontend Next.js (Fase A) | 🔵 Em andamento |
| **Must** | Streaming + cartões visuais | 🔵 Em andamento |
| **Must** | Observabilidade (LangSmith) | 🔵 Em andamento |
| **Should** | Evals em CI + RAGAS (Fase B) | 🔲 |
| **Should** | Rate limit + cost engineering | 🔲 |
| **Could** | Auth + persistência (Fase C) | 🔲 |
| **Could** | PDF de carta | 🔲 |
| **Won't (agora)** | Áudio, integrações externas, mobile | 🔲 |

---

*Ritmo real > cronograma teórico. Atualize este arquivo ao final de cada sprint.*
