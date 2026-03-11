# Guia de Deploy — Resolve Aí 🚀

Este documento descreve os passos para realizar o deploy do Resolve Aí no **Google Cloud Run**.

## Pré-requisitos

1.  **Google Cloud SDK (gcloud CLI)**: [Instruções de Instalação](https://cloud.google.com/sdk/docs/install?hl=pt-br)
2.  **Docker**: Instalado e configurado.
3.  **Projeto Google Cloud**: ID do projeto com faturamento ativado.
4.  **Google API Key**: Chave do Gemini configurada.

## Passo a Passo

### 1. Autenticação e Configuração Inicial

```bash
# Login no Google Cloud
gcloud auth login

# Configurar o projeto padrão
gcloud config set project [PROJECT_ID]

# Ativar APIs necessárias
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

### 2. Preparar Artifact Registry

```bash
# Criar repositório para o Docker
gcloud artifacts repositories create resolve-ai-repo \
    --repository-format=docker \
    --location=southamerica-east1 \
    --description="Docker repository for Resolve Ai"

# Configurar autenticação do Docker
gcloud auth configure-docker southamerica-east1-docker.pkg.dev
```

### 3. Build e Push da Imagem

```bash
# Build local da imagem
docker build -t southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/app:latest .

# Push para o registro
docker push southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/app:latest
```

### 4. Deploy no Cloud Run

```bash
gcloud run deploy resolve-ai \
    --image southamerica-east1-docker.pkg.dev/[PROJECT_ID]/resolve-ai-repo/app:latest \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_API_KEY=[SUA_CHAVE_AQUI],GRADIO_SERVER_PORT=8080"
```

## Salvaguardas em Produção

- **Autenticação**: O Gradio está configurado com usuário/senha no arquivo `frontend/app.py`.
- **Limites de Tokens**: O backend possui limites para evitar custos excessivos.
- **Porta**: O Cloud Run exige que o container escute na porta `8080` (configurado via `GRADIO_SERVER_PORT`).

---

*Nota: Substitua `[PROJECT_ID]` pelo ID real do seu projeto Google Cloud.*
