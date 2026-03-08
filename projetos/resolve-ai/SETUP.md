# Setup do Ambiente — Resolve Aí 🔧

> Guia passo a passo para configurar o ambiente de desenvolvimento.

---

## Pré-requisitos

| Ferramenta | Versão Mínima | Para que serve |
|-----------|:-------------:|----------------|
| **Python** | 3.11+ | Backend, agentes, RAG |
| **Node.js** | 18+ | Frontend Next.js |
| **Git** | 2.x | Controle de versão |
| **Docker** | 24+ | Containerização e ChromaDB |
| **Google Cloud SDK** | Latest | Deploy e Vertex AI (opcional para dev) |

---

## 1. Clone e Estrutura Inicial

```bash
# Crie o repositório e clone
git clone https://github.com/seu-usuario/resolve-ai.git
cd resolve-ai

# Crie a estrutura de pastas
mkdir -p agents rag/{ingestion,retrieval,vector_store} api/{routes,schemas} \
         frontend data/{cdc,jurisprudence,procon} evaluation tests/{unit,integration} docs
```

---

## 2. Python — Ambiente Virtual

### Opção A: venv (simples)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install --upgrade pip
```

### Opção B: pyenv + venv (recomendado para múltiplos projetos)

```bash
# Instale o pyenv (Windows: pyenv-win)
# https://github.com/pyenv-win/pyenv-win

pyenv install 3.11.9
pyenv local 3.11.9
python -m venv .venv
.venv\Scripts\activate
```

> 💡 **Dica de Sênior:** Sempre use `.python-version` (pyenv) ou `.tool-versions` (asdf) no repositório para que todos usem a mesma versão do Python. Isso evita o clássico "funciona na minha máquina".

---

## 3. Dependências Python

### requirements.txt (MVP)

```txt
# Core
fastapi==0.115.*
uvicorn[standard]==0.34.*
pydantic==2.*

# LLM & Agents
langgraph==0.4.*
langchain==0.3.*
langchain-google-genai==2.*
google-genai==1.*

# RAG
llama-index==0.12.*
chromadb==0.5.*

# Utilitários
python-dotenv==1.*
httpx==0.28.*

# Dev & Testes
pytest==8.*
pytest-asyncio==0.24.*
ruff==0.8.*
mypy==1.13.*

# Avaliação (opcional, para Fase 2)
# ragas==0.2.*
```

```bash
pip install -r requirements.txt
```

> ⚠️ **Nota:** As versões acima são sugestões. Antes de instalar, verifique as versões mais recentes no PyPI. O ecossistema LLM muda rapidamente.

---

## 4. Variáveis de Ambiente

### .env.example

```env
# === LLM ===
LLM_PROVIDER=gemini                    # gemini | ollama
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-1.5-flash

# === Ollama (dev local) ===
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# === Vector Store ===
VECTOR_STORE=chroma                    # chroma | vertex
CHROMA_PERSIST_DIR=./data/chroma_db

# === Google Cloud (prod) ===
GOOGLE_PROJECT_ID=seu-projeto
GOOGLE_REGION=us-central1

# === API ===
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000

# === Misc ===
LOG_LEVEL=INFO
ENVIRONMENT=development               # development | production
```

```bash
# Copie o exemplo e preencha suas chaves
cp .env.example .env
```

> 💡 **Dica de Sênior:** NUNCA commite o `.env`. Adicione-o ao `.gitignore` imediatamente. Use `.env.example` sem valores reais como documentação das variáveis necessárias.

---

## 5. Chaves de API

### Gemini API Key

1. Acesse [Google AI Studio](https://aistudio.google.com/)
2. Clique em **"Get API Key"**
3. Crie uma nova chave ou use uma existente
4. Cole no `.env` como `GEMINI_API_KEY`

### Google Cloud (para deploy)

```bash
# Instale o Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Autentique
gcloud auth login
gcloud config set project SEU_PROJETO

# Habilite as APIs necessárias
gcloud services enable run.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

---

## 6. ChromaDB Local

### Via Docker (recomendado)

```bash
docker run -d \
  --name chromadb \
  -p 8001:8000 \
  -v ./data/chroma_db:/chroma/chroma \
  chromadb/chroma:latest
```

### Via pip (mais simples para dev)

ChromaDB pode rodar in-process (sem servidor separado):

```python
import chromadb

# Persistente em disco
client = chromadb.PersistentClient(path="./data/chroma_db")

# Ou em memória (para testes)
client = chromadb.Client()
```

> 💡 **Dica de Sênior:** Para o MVP, use ChromaDB in-process (PersistentClient). Não precisa de Docker só para o vector store em dev. Docker fica para quando quiser rodar tudo junto (docker-compose) ou para simular o ambiente de produção.

---

## 7. Ollama (LLM Local — Opcional)

Para desenvolver sem gastar créditos da API Gemini:

```bash
# Instale o Ollama
# https://ollama.com/download

# Baixe um modelo leve
ollama pull llama3.2

# Teste
ollama run llama3.2 "Olá, o que é o CDC?"
```

Ollama roda na porta `11434` por padrão. Configure no `.env`:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

> 💡 **Dica de Sênior:** Use Ollama no dia a dia do desenvolvimento para iterar rápido sem custo. Troque para Gemini apenas para testes de qualidade e antes do deploy. Um `LLM_PROVIDER` factory no código torna essa troca transparente.

---

## 8. Frontend (Next.js)

```bash
cd frontend

# Crie o projeto Next.js
npx -y create-next-app@latest ./ --typescript --eslint --app --src-dir --no-tailwind

# Instale e rode
npm install
npm run dev
```

O frontend (temporário) estaria em `http://localhost:3000`.

> ⚠️ **Nota Histórica:** Na Sprint 3, pivotamos o desenvolvimento do Chat UI inteiramente para **Gradio 6**, para agilizar o MVP. O React/Next.js será reintroduzido na **Fase 3 (Escala)**.

---

## 9. Docker Compose (Tudo Junto)

### docker-compose.yml

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - chromadb
    volumes:
      - ./data:/app/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  chroma_data:
```

```bash
# Suba tudo
docker compose up -d

# Veja os logs
docker compose logs -f backend
```

---

## 10. Verificação do Setup

Execute este checklist para confirmar que tudo está funcionando:

```bash
# 1. Python
python --version          # 3.11+
pip list | grep fastapi   # fastapi instalado

# 2. Servidor FastAPI
uvicorn api.main:app --reload
# → http://localhost:8000/docs (Swagger UI)

# 3. ChromaDB
python -c "import chromadb; print(chromadb.__version__)"

# 4. Gemini API
python -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
print(model.generate_content('Diga olá').text)
"

# 5. Frontend
# Nota: O MVP possui uma trava de segurança. O login padrão é visitante / resolveai
# Se quiser customizar, passe a variável de ambiente:
# export GRADIO_AUTH="usuario:senha"
uv run python frontend/app.py
# → http://localhost:7860

# 6. Testes
pytest tests/ -v
```

---

## Troubleshooting Comum

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError` | Verifique se o venv está ativado: `which python` |
| ChromaDB `Permission denied` | Verifique permissões da pasta `data/chroma_db` |
| Gemini `403 Forbidden` | Chave API inválida ou quota excedida |
| Ollama `Connection refused` | Rode `ollama serve` antes de usar |
| Next.js `ENOENT` | Rode `npm install` dentro de `frontend/` |

---

*Após configurar, leia o [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) para entender o fluxo de trabalho.*
