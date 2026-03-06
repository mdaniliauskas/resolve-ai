# Referências e Recursos — Resolve Aí 📚

> Papers, cursos, documentação e ferramentas organizados por tema.

---

## 1. Papers Acadêmicos

### Fundamentais (leitura obrigatória)

| Paper | Ano | Por que ler | Link |
|-------|:---:|-------------|------|
| **Attention Is All You Need** | 2017 | Fundamento dos Transformers (arquitetura base de todos os LLMs) | [arXiv](https://arxiv.org/abs/1706.03762) |
| **ReAct: Synergizing Reasoning and Acting** | 2022 | Padrão de agentes que raciocinam e agem — base do LangGraph | [arXiv](https://arxiv.org/abs/2210.03629) |
| **Retrieval-Augmented Generation for Knowledge-Intensive NLP** | 2020 | Paper original do RAG (Meta) | [arXiv](https://arxiv.org/abs/2005.11401) |

### Avançados (leitura recomendada)

| Paper | Ano | Por que ler | Link |
|-------|:---:|-------------|------|
| **LoRA: Low-Rank Adaptation** | 2021 | Fine-tuning eficiente de LLMs | [arXiv](https://arxiv.org/abs/2106.09685) |
| **RAG Survey** | 2023 | Visão panorâmica de técnicas RAG | [arXiv](https://arxiv.org/abs/2312.10997) |
| **Self-RAG** | 2023 | RAG com auto-reflexão | [arXiv](https://arxiv.org/abs/2310.11511) |
| **HyDE: Hypothetical Document Embeddings** | 2022 | Melhora retrieval gerando documento hipotético | [arXiv](https://arxiv.org/abs/2212.10496) |
| **Chain-of-Thought Prompting** | 2022 | Raciocínio passo a passo em LLMs | [arXiv](https://arxiv.org/abs/2201.11903) |

### Como ler um paper de IA (dica prática)

```
1. Leia o Abstract (2 min)
2. Leia a Introdução e a Conclusão (10 min)
3. Olhe as figuras e tabelas (5 min)
4. Se relevante, leia a Metodologia (20 min)
5. Procure blog posts explicativos (ex: Jay Alammar) para intuição visual
```

---

## 2. Cursos Gratuitos

### DeepLearning.AI (Andrew Ng) — Cursos Curtos

| Curso | Duração | Relevância | Link |
|-------|:-------:|:----------:|------|
| **Building & Evaluating Advanced RAG** | 1h | 🔴 Essencial | [deeplearning.ai](https://www.deeplearning.ai/short-courses/building-evaluating-advanced-rag/) |
| **AI Agents in LangGraph** | 1h | 🔴 Essencial | [deeplearning.ai](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) |
| **Evaluating and Debugging Generative AI** | 1h | 🟡 Importante | [deeplearning.ai](https://www.deeplearning.ai/short-courses/evaluating-debugging-generative-ai/) |
| **LangChain for LLM Application Development** | 1h | 🟡 Importante | [deeplearning.ai](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/) |
| **Functions, Tools and Agents with LangChain** | 1h | 🟢 Complementar | [deeplearning.ai](https://www.deeplearning.ai/short-courses/functions-tools-agents-langchain/) |

### Google Cloud

| Recurso | Relevância | Link |
|---------|:----------:|------|
| **GenAI Learning Path** | 🔴 Essencial | [Cloud Skills Boost](https://www.cloudskillsboost.google/paths/183) |
| **Vertex AI Generative AI Studio** | 🟡 Importante | [Google Cloud Docs](https://cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts) |

### Udemy

| Curso | Instrutor | Relevância |
|-------|-----------|:----------:|
| **LLM Engineering: Master AI & LLMs** | Ed Donner | 🔴 Em andamento |

---

## 3. Livros

| Livro | Autor | Por que ler |
|-------|-------|-------------|
| **Build a Large Language Model (From Scratch)** | Sebastian Raschka | Entendimento profundo de como LLMs funcionam |
| **Designing Machine Learning Systems** | Chip Huyen | System design para ML (arquitetura, deploy, monitoring) |
| **Natural Language Processing with Transformers** | Lewis Tunstall et al. | Prática com Transformers (HuggingFace) |

---

## 4. Documentação Oficial

### Core Stack

| Tecnologia | Docs | Notas |
|-----------|------|-------|
| **LangGraph** | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/) | Foco em StateGraph, nodes, edges |
| **LangChain** | [python.langchain.com](https://python.langchain.com/) | Usar seletivamente (retrievers, embeddings) |
| **FastAPI** | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) | Excelente docs, com tutorial interativo |
| **ChromaDB** | [docs.trychroma.com](https://docs.trychroma.com/) | Simples e direto |
| **Pydantic v2** | [docs.pydantic.dev](https://docs.pydantic.dev/) | Mudanças significativas do v1 para v2 |
| **Google Generative AI** | [ai.google.dev](https://ai.google.dev/gemini-api/docs) | API do Gemini |
| **Vertex AI** | [cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai/docs) | Deploy e Vector Search |

### Avaliação

| Ferramenta | Docs | Para que serve |
|-----------|------|----------------|
| **RAGAS** | [docs.ragas.io](https://docs.ragas.io/) | Métricas de avaliação de RAG |
| **LangSmith** | [docs.smith.langchain.com](https://docs.smith.langchain.com/) | Tracing e debugging de LLM |

---

## 5. Blogs e Conteúdo Visual

| Recurso | Tipo | Por que seguir |
|---------|:----:|----------------|
| **Jay Alammar** | Blog | Visualizações incríveis de Transformers e Embeddings |
| **LiLian Weng** (OpenAI) | Blog | Surveys profundos e bem escritos |
| **Chip Huyen** | Blog/Substack | MLOps, system design para ML |
| **ByteByteGo** | YouTube | System design visual e acessível |
| **3Blue1Brown** | YouTube | Intuição matemática (neural nets, transformers) |
| **Andrej Karpathy** | YouTube | Explicações de GPT, tokenização, nanoGPT |

---

## 6. Repositórios de Referência

| Repositório | Para que serve | Link |
|-------------|----------------|------|
| **LangGraph Examples** | Exemplos oficiais de multi-agent | [GitHub](https://github.com/langchain-ai/langgraph/tree/main/examples) |
| **RAG Tutorial (LlamaIndex)** | Tutorial completo de RAG | [GitHub](https://github.com/run-llama/llama_index/tree/main/docs/docs/examples) |
| **Full-Stack FastAPI Template** | Template de FastAPI production-ready | [GitHub](https://github.com/fastapi/full-stack-fastapi-template) |
| **RAGAS** | Framework de avaliação | [GitHub](https://github.com/explodinggradients/ragas) |

---

## 7. Legislação — Fontes do CDC

| Fonte | Formato | Link |
|-------|:-------:|------|
| **CDC — Planalto** | HTML/TXT | [planalto.gov.br](https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm) |
| **CDC — JusBrasil** | HTML | [jusbrasil.com.br](https://www.jusbrasil.com.br/legislacao/91585/codigo-de-defesa-do-consumidor-lei-8078-90) |
| **Decreto 2.181/97** | HTML | [planalto.gov.br](https://www.planalto.gov.br/ccivil_03/decreto/d2181.htm) |
| **consumidor.gov.br** | Portal | [consumidor.gov.br](https://www.consumidor.gov.br/) |

---

## 8. Ferramentas de Desenvolvimento

| Ferramenta | Para que serve | Link |
|-----------|----------------|------|
| **Ollama** | Rodar LLMs localmente | [ollama.com](https://ollama.com/) |
| **Docker Desktop** | Containerização | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Postman / Insomnia** | Testar APIs REST | [postman.com](https://www.postman.com/) |
| **Ruff** | Linting Python ultra-rápido | [docs.astral.sh/ruff](https://docs.astral.sh/ruff/) |
| **mypy** | Type checking Python | [mypy-lang.org](https://mypy-lang.org/) |

---

## 9. Comunidades

| Comunidade | Plataforma | Link |
|-----------|:----------:|------|
| **LangChain Discord** | Discord | [discord.gg/langchain](https://discord.gg/langchain) |
| **MLOps Community** | Slack | [mlops.community](https://mlops.community/) |
| **r/LocalLLaMA** | Reddit | [reddit.com/r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) |
| **r/MachineLearning** | Reddit | [reddit.com/r/MachineLearning](https://www.reddit.com/r/MachineLearning/) |

---

*Atualize este documento conforme descobrir novos recursos relevantes.*
