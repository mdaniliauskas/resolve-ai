# Session State — Resolve Aí

> Arquivo de checkpoint gerado ao fim de cada sessão produtiva.
> A próxima sessão deve começar lendo este arquivo.

---

## Estado em: 2026-05-06

### O que foi entregue (Sprint A1 — COMPLETO ✅)

1. **Frontend Next.js 16** migrado de Gradio — App Router, Tailwind 4, shadcn/ui
2. **SSE streaming** — LangGraph `.stream()` → FastAPI `StreamingResponse` → Next.js `ReadableStream`
3. **Visual cards** — artigos CDC (verde), canais de resolução (azul), precedentes STJ
4. **Markdown rendering** — `react-markdown` + `remark-gfm` + `@tailwindcss/typography`
5. **Two-service Cloud Run** — `resolve-ai-api` (FastAPI) + `resolve-ai-web` (Next.js)
6. **CVEs zerados** — `uv lock --upgrade` → docker scout `0C 0H 0M 0L`
7. **CORS configurado** com URL de produção do frontend
8. **ADR-014 documentado** — decisão Cloud Run vs Vercel
9. **README atualizado** — stack atual, URLs live, status correto

### URLs de produção

| Serviço | URL |
|---------|-----|
| Backend (FastAPI) | https://resolve-ai-444080754389.southamerica-east1.run.app |
| Frontend (Next.js) | https://resolve-ai-web-444080754389.southamerica-east1.run.app |
| GCP Project | `resolve-ai-daniliauskas` · região `southamerica-east1` |
| Artifact Registry | `southamerica-east1-docker.pkg.dev/resolve-ai-daniliauskas/resolve-ai-repo/` |

### Git — último commit

```
e87b714  fix(deps): upgrade pillow/aiohttp/nltk/langchain-core to patch HIGH CVEs
```

Branch: `main` — em sync com GitHub `mdaniliauskas/resolve-ai`

---

## Próxima sessão: Sprint A2

### Tarefas pendentes (em ordem de prioridade)

- [ ] **LangSmith** — instrumentar o pipeline LangGraph (ADR-012 para decidir LangSmith vs Phoenix)
- [ ] **structlog** — substituir `print()` por logs estruturados no backend
- [ ] **Mover Gradio para `frontend-legacy/`** — manter código mas tirar do path principal
- [ ] **GitHub description** — atualizar descrição do repo para vitrine pública

### Decisões em aberto que afetam A2

| ADR | Decisão | Prazo |
|-----|---------|-------|
| ADR-012 | Observabilidade: LangSmith vs Phoenix/Arize | **Fase A — urgente** |

### Como retomar

1. Leia este arquivo
2. Acesse o frontend em produção para confirmar que está no ar
3. Siga com ADR-012 antes de implementar observabilidade

---

## Estrutura de arquivos críticos

```
agents/workflow.py          # Pipeline LangGraph + stream_chat()
api/routes.py               # /api/chat/stream (SSE)
web/components/chat/        # ChatInterface, MessageBubble, ExampleCards
web/types/chat.ts           # Tipos TypeScript compartilhados
config.py                   # Settings (lê .env / env vars)
Dockerfile                  # Backend
Dockerfile.web              # Frontend (standalone)
deploy.md                   # Guia de deploy com URLs reais
projetos/resolve-ai/TECH_DECISIONS.md  # ADRs
projetos/resolve-ai/ROADMAP.md         # Fases A/B/C/D
```
