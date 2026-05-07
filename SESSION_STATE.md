# Session State — Resolve Aí

> Arquivo de checkpoint gerado ao fim de cada sessão produtiva.
> A próxima sessão deve começar lendo este arquivo.

---

## Estado em: 2026-05-07

### O que foi entregue (Sprint A2 — COMPLETO ✅)

1. **Modelo corrigido** — `gemini-3.1-flash` em `config.py` e `.env.example`
2. **Tema emerald** — tokens CSS (`--primary`, `--accent`, `--ring`) alinhados ao emerald-700 dos componentes
3. **structlog** — `logging_config.py` criado; JSON em produção, console colorido em dev; `api/main.py` atualizado
4. **LangSmith ativo em produção** — vars injetadas no Cloud Run (revisão `resolve-ai-00006`); traces chegando em `smith.langchain.com`
5. **Gradio → `frontend-legacy/`** — movido via `git mv`, referências em `CLAUDE.md` atualizadas
6. **GitHub CLI instalado e autenticado** — `gh` disponível para operações de repo
7. **GitHub description atualizada** — vitrine pública bilíngue
8. **README atualizado** — Sprint A2 marcada como concluída
9. **uv update** — ~30 pacotes atualizados (langgraph 1.1.10, fastapi 0.136, google-genai 1.75)

### URLs de produção

| Serviço | URL |
|---------|-----|
| Backend (FastAPI) | https://resolve-ai-444080754389.southamerica-east1.run.app |
| Frontend (Next.js) | https://resolve-ai-web-444080754389.southamerica-east1.run.app |
| LangSmith | https://smith.langchain.com — projeto `Resolve Ai` |
| GCP Project | `resolve-ai-daniliauskas` · região `southamerica-east1` |
| Artifact Registry | `southamerica-east1-docker.pkg.dev/resolve-ai-daniliauskas/resolve-ai-repo/` |

### Git — últimos commits

```
(este commit)  docs: close Sprint A2 — LangSmith live, README final
d583938        docs: session checkpoint A2 in progress
6ac47f7        docs: update README status (Sprint A2 in progress) and model name
c6d0d05        refactor: move Gradio to frontend-legacy/, update CLAUDE.md references
40da3a7        feat(observability): add structlog + LangSmith wiring, fix model name, brand theme
```

Branch: `main` — em sync com GitHub `mdaniliauskas/resolve-ai`

---

## Próxima sessão: Sprint B

### Tarefas pendentes

- [ ] **RAG quality** — re-ranking dos chunks CDC (ADR a decidir: Cohere Rerank vs cross-encoder local)
- [ ] **Eval harness** — baseline RAGAS sobre o golden set (`tests/test_golden_set.py`)
- [ ] **gcloud via cmd.exe** — para próximos deploys, usar cmd.exe do Windows (Git Bash tem bug SSL no gcloud)

### Como retomar

1. Leia este arquivo
2. Confirme LangSmith recebendo traces: `smith.langchain.com` → projeto `Resolve Ai`
3. Siga com Sprint B — RAG quality

---

## Estrutura de arquivos críticos

```
agents/workflow.py          # Pipeline LangGraph + stream_chat()
api/routes.py               # /api/chat/stream (SSE)
api/main.py                 # Startup + structlog
logging_config.py           # Configuracao structlog (novo)
web/components/chat/        # ChatInterface, MessageBubble, ExampleCards
web/app/globals.css         # Tokens CSS emerald (atualizado)
config.py                   # Settings (le .env / env vars)
Dockerfile                  # Backend
Dockerfile.web              # Frontend (standalone)
deploy.md                   # Guia de deploy com URLs reais
projetos/resolve-ai/TECH_DECISIONS.md  # ADRs
projetos/resolve-ai/ROADMAP.md         # Fases A/B/C/D
```
