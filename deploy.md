# Guia de Deploy — Resolve Aí 🚀

Dois serviços no **Google Cloud Run** (região `southamerica-east1`):

| Serviço | Imagem | Porta | Dockerfile |
|---------|--------|-------|------------|
| `resolve-ai-api` | FastAPI + LangGraph + ChromaDB | 8080 | `Dockerfile` |
| `resolve-ai-web` | Next.js 16 | 8080 | `Dockerfile.web` |

---

## Variáveis de ambiente necessárias

| Serviço | Variável | Valor |
|---------|----------|-------|
| `resolve-ai-api` | `GOOGLE_API_KEY` | Chave do Gemini |
| `resolve-ai-web` | `BACKEND_URL` | URL do serviço `resolve-ai-api` |

---

## Passo a Passo

### 1. Autenticação e configuração

```bash
gcloud auth login
gcloud config set project [PROJECT_ID]
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

### 2. Criar Artifact Registry (só na primeira vez)

```bash
gcloud artifacts repositories create resolve-ai-repo \
    --repository-format=docker \
    --location=southamerica-east1

gcloud auth configure-docker southamerica-east1-docker.pkg.dev
```

### 3. Deploy do backend (FastAPI)

```bash
# Build e push
docker build -t southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/api:latest .
docker push southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/api:latest

# Deploy
gcloud run deploy resolve-ai-api \
    --image southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/api:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_API_KEY=[SUA_CHAVE_AQUI]"
```

Anote a URL gerada — será usada como `BACKEND_URL` no próximo passo.

### 4. Deploy do frontend (Next.js)

```bash
# Build e push
docker build -f Dockerfile.web \
    -t southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/web:latest .
docker push southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/web:latest

# Deploy (substitua BACKEND_URL pela URL do passo anterior)
gcloud run deploy resolve-ai-web \
    --image southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/web:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --set-env-vars="BACKEND_URL=https://resolve-ai-api-xxxx-uc.a.run.app"
```

### 5. Atualizar CORS no backend

Depois de obter a URL do frontend, adicione-a às origens permitidas:

```bash
gcloud run services update resolve-ai-api \
    --region southamerica-east1 \
    --set-env-vars="GOOGLE_API_KEY=[CHAVE],API_CORS_ORIGINS=https://resolve-ai-web-xxxx-uc.a.run.app"
```

---

## Re-deploy rápido (atualização de código)

```bash
# Backend
docker build -t southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/api:latest . \
  && docker push southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/api:latest \
  && gcloud run deploy resolve-ai-api --image southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/api:latest --region southamerica-east1

# Frontend
docker build -f Dockerfile.web -t southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/web:latest . \
  && docker push southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/web:latest \
  && gcloud run deploy resolve-ai-web --image southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/web:latest --region southamerica-east1
```

---

*Substitua `[PROJECT_ID]` pelo ID real do projeto Google Cloud.*
