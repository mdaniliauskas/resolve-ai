# Resolve Aí 🛡️

> Seu assistente inteligente para dúvidas sobre o Código de Defesa do Consumidor

---

## 🎯 O Problema

Consumidores brasileiros frequentemente **não sabem se seu problema é amparado pelo CDC**, por onde começar a reclamar, qual canal tem mais chance de resolução rápida, ou quando escalar para instâncias formais. O resultado: tempo perdido, frustração e direitos não exercidos.

## 💡 A Solução

O **Resolve Aí** é um chatbot inteligente com arquitetura **multi-agentes + RAG** que:

1. **Analisa** se o caso se enquadra no CDC e identifica artigos aplicáveis
2. **Classifica** o tipo de problema (defeito, cobrança indevida, propaganda enganosa, etc.)
3. **Orienta** com uma estratégia personalizada de resolução
4. **Encaminha** com links e instruções concretas para os canais mais adequados

### Fluxo de Encaminhamento

| Etapa | Canal | Quando usar |
|:-----:|-------|-------------|
| 1ª | Contato direto com a empresa | Sempre como primeiro passo |
| 2ª | Ouvidoria da empresa | Quando o SAC não resolver |
| 3ª | [consumidor.gov.br](https://www.consumidor.gov.br) | Plataforma oficial do governo |
| 4ª | PROCON estadual/municipal | Quando as anteriores falharem |
| 5ª | Juizado Especial Cível (JEC) | Casos sem solução extrajudicial |

---

## 🧠 Arquitetura (Visão Geral)

O sistema utiliza **4 agentes especializados** orquestrados por LangGraph, alimentados por uma base de conhecimento RAG do CDC:

```
Usuário → Interface Chat/Web
                │
                ▼
        Agente Orquestrador ──→ coordena fluxo
           │           │
           ▼           ▼
       RAG CDC    Ag. Análise Jurídica ──→ identifica enquadramento
           │           │
           └─────┬─────┘
                 ▼
         Ag. Estratégia ──→ monta plano de ação
                 │
                 ▼
         Ag. Resposta ──→ formata resposta final
```

> 📐 Arquitetura completa com diagramas Mermaid em [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## ⚙️ Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| **LLM** | Gemini 1.5 Flash (via Vertex AI / API direta) |
| **Orquestração de Agentes** | LangGraph |
| **RAG / Embeddings** | LlamaIndex + ChromaDB (dev) → Vertex AI Vector Search (prod) |
| **Backend** | Python + FastAPI |
| **Frontend** | Next.js |
| **Deploy** | Docker + Google Cloud Run |

---

## 📁 Estrutura do Projeto

```
resolve-ai/
├── agents/                  # Agentes de IA (LangGraph)
│   ├── orchestrator.py      # Orquestrador principal
│   ├── legal_analysis.py    # Análise jurídica
│   ├── strategy.py          # Estratégia de encaminhamento
│   └── response.py          # Formatação de resposta
├── rag/                     # Pipeline RAG
│   ├── ingestion/           # Ingestão de documentos
│   ├── retrieval/           # Busca e ranking
│   └── vector_store/        # Configuração ChromaDB
├── api/                     # Backend FastAPI
│   ├── routes/              # Endpoints REST
│   └── schemas/             # Modelos Pydantic
├── frontend/                # Next.js
├── data/                    # Fontes de conhecimento
│   ├── cdc/                 # Texto do CDC
│   ├── jurisprudence/       # Jurisprudência (Fase 2)
│   └── procon/              # Base PROCON (Fase 2)
├── evaluation/              # Notebooks de avaliação RAGAS
├── tests/                   # Testes unitários e integração
├── docs/                    # Especificações e documentação
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Status do Projeto

**Fase atual:** Pré-MVP (planejamento e documentação concluídos)

| Fase | Status | Descrição |
|------|:------:|-----------|
| **MVP** | 🔲 | Chat + RAG CDC + Agente de análise + Encaminhamento |
| **Enriquecimento** | 🔲 | Jurisprudência + Estratégia avançada + Histórico + PDF |
| **Escala** | 🔲 | Integração gov.br + Cartas automáticas + App mobile |

> 📋 Roadmap detalhado em [ROADMAP.md](./ROADMAP.md)

---

## 📚 Documentação Completa

| Documento | Descrição |
|-----------|-----------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Arquitetura detalhada com diagramas Mermaid |
| [SETUP.md](./SETUP.md) | Guia de setup do ambiente de desenvolvimento |
| [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) | Guia de desenvolvimento + dicas de sênior |
| [TECH_DECISIONS.md](./TECH_DECISIONS.md) | Decisões técnicas (ADRs) |
| [MVP_SPEC.md](./MVP_SPEC.md) | Especificação técnica do MVP |
| [ROADMAP.md](./ROADMAP.md) | Roadmap com milestones e critérios |
| [PROMPTS_GUIDE.md](./PROMPTS_GUIDE.md) | Prompts para desenvolvimento assistido por IA |
| [REFERENCES.md](./REFERENCES.md) | Papers, cursos e recursos de referência |

---

## 📄 Base Legal

Baseado na **Lei nº 8.078/1990** (Código de Defesa do Consumidor) e normas do SNDC.

> ⚠️ O Resolve Aí oferece orientação informativa e **não substitui assessoria jurídica profissional**. Para casos complexos, recomenda-se consultar um advogado.

---

## 🧑‍💻 Contexto do Desenvolvedor

Este projeto é desenvolvido por alguém com:
- **Doutorado em Sociologia** → rigor metodológico, avaliação de vieses, pesquisa qualitativa/quantitativa
- **ADS pela FATEC SP** → base sólida em Engenharia de Software
- **Curso de LLM Engineering** (Ed Donner / Udemy) → RAG, Fine-tuning, Agents
- **Google Cloud credits** → deploy e experimentação em Vertex AI

O projeto serve como **carro-chefe do portfólio** para uma vaga de Desenvolvedor/Pesquisador GenAI.

---

*Resolve Aí — Seu direito, do jeito mais fácil.* 🇧🇷
