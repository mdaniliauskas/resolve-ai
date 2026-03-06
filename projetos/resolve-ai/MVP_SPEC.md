# Especificação Técnica do MVP — Resolve Aí 📐

> Fase 1: Chat funcional + RAG do CDC + Agente de análise jurídica + Encaminhamento básico.

---

## 1. Escopo do MVP

### Incluído ✅

| Feature | Descrição |
|---------|-----------|
| **Chat simples** | Usuário digita situação, recebe orientação |
| **RAG do CDC** | Base do CDC completa com retrieval |
| **Análise jurídica** | Identifica artigos e direitos aplicáveis |
| **Encaminhamento** | Sugere canais de resolução (escada padrão) |
| **API REST** | Endpoint `/api/chat` documentado |
| **Interface web** | Chat mínimo funcional |

### Excluído ❌ (Fases seguintes)

| Feature | Fase |
|---------|:----:|
| Histórico de conversas | 2 |
| Jurisprudência no RAG | 2 |
| Exportação em PDF | 2 |
| Autenticação | 2 |
| Integração consumidor.gov.br | 3 |
| Geração de cartas/e-mails | 3 |
| App mobile | 3 |

---

## 2. Funcionalidades Detalhadas

### 2.1 Chat — Fluxo Principal

**Ator:** Consumidor

**Fluxo feliz:**
1. Consumidor acessa o site
2. Vê tela de chat com mensagem de boas-vindas e disclaimer legal
3. Digita sua situação: _"Comprei um celular e a tela quebrou com 10 dias"_
4. Sistema analisa e responde com:
   - Se o caso se enquadra no CDC ✅/❌
   - Artigos aplicáveis (ex: Art. 18 — Vícios do Produto)
   - Direitos do consumidor neste caso
   - Passos concretos para resolução (1. Contate a loja → 2. Ouvidoria → ...)
   - Links úteis (consumidor.gov.br, PROCON da região)
5. Consumidor pode fazer perguntas de acompanhamento na mesma sessão

**Fluxos alternativos:**
- **Caso fora do CDC:** Responde de forma empática explicando que não é coberto e sugere onde buscar ajuda (ex: Justiça do Trabalho)
- **Caso ambíguo:** Explica o enquadramento com ressalvas e recomenda buscar advogado
- **Input vazio/irrelevante:** Mensagem gentil pedindo para descrever a situação

### 2.2 Critérios de Aceite

| ID | Critério | Verificação |
|:--:|----------|-------------|
| CA-01 | O sistema responde em menos de 15 segundos | Medir latência end-to-end |
| CA-02 | A resposta cita artigos do CDC quando aplicável | Verificar nos top 20 casos comuns |
| CA-03 | A resposta inclui passos acionáveis | Verificar presença de lista numerada |
| CA-04 | Casos fora do CDC recebem resposta adequada | Testar com 5 casos não-CDC |
| CA-05 | A API retorna status 200 para requests válidos | Teste automatizado |
| CA-06 | A API retorna status 422 para requests inválidos | Testar com body vazio |
| CA-07 | O disclaimer legal é visível na interface | Verificação visual |
| CA-08 | CORS está configurado corretamente | Testar cross-origin request |

---

## 3. Especificação da API

### POST /api/chat

**Request:**
```json
{
  "message": "Comprei um celular e a tela quebrou com 10 dias de uso"
}
```

**Response (200):**
```json
{
  "response": "Seu caso se enquadra no Código de Defesa do Consumidor...",
  "analysis": {
    "is_cdc_case": true,
    "articles": [
      {
        "number": "Art. 18",
        "title": "Responsabilidade por Vício do Produto",
        "relevance": "O produto apresentou defeito dentro do prazo de garantia legal (90 dias)"
      }
    ],
    "rights": [
      "Reparo em até 30 dias",
      "Substituição do produto",
      "Devolução do valor pago"
    ],
    "severity": "medium"
  },
  "strategy": {
    "channels": [
      {
        "step": 1,
        "name": "Contato com a loja",
        "description": "Entre em contato com a loja onde comprou",
        "link": null
      },
      {
        "step": 2,
        "name": "consumidor.gov.br",
        "description": "Registre reclamação na plataforma do governo",
        "link": "https://www.consumidor.gov.br"
      },
      {
        "step": 3,
        "name": "PROCON",
        "description": "Procure o PROCON da sua cidade/estado",
        "link": "https://www.procon.sp.gov.br"
      }
    ]
  },
  "sources": [
    "CDC Art. 18 - Seção III - Da Responsabilidade por Vício do Produto e do Serviço"
  ],
  "metadata": {
    "model": "gemini-1.5-flash",
    "latency_ms": 3200,
    "tokens_used": 850
  }
}
```

**Response (422 — Validation Error):**
```json
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["body", "message"],
      "msg": "Input should be a valid string"
    }
  ]
}
```

### GET /api/health

**Response (200):**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "llm_provider": "gemini",
  "vector_store": "chroma"
}
```

---

## 4. Prompt Templates dos Agentes

### 4.1 Orquestrador — Classificação de Intenção

```
Você é um assistente especializado em Direito do Consumidor brasileiro.

Classifique a mensagem do usuário em UMA das categorias:
- "consumer_complaint": O usuário descreve um problema com produto ou serviço
- "general_question": O usuário tem uma dúvida sobre o CDC ou direitos do consumidor
- "greeting": O usuário está cumprimentando ou fazendo conversa casual
- "out_of_scope": A mensagem não tem relação com consumo ou direitos do consumidor

Mensagem do usuário: {user_message}

Responda APENAS com a categoria, sem explicações.
```

### 4.2 Análise Jurídica

```
Você é um especialista em Direito do Consumidor brasileiro com profundo conhecimento
do Código de Defesa do Consumidor (Lei 8.078/1990).

Com base no contexto jurídico abaixo e na situação descrita pelo consumidor, determine:

1. Se a situação se enquadra no CDC (sim/não)
2. Quais artigos são aplicáveis (liste os números e títulos)
3. Quais direitos o consumidor possui neste caso
4. A gravidade do caso: "low" (inconveniente menor), "medium" (prejuízo moderado), "high" (dano significativo)
5. Sua confiança na análise (0.0 a 1.0)

## Contexto Jurídico (CDC):
{rag_context}

## Situação do Consumidor:
{user_message}

## Instruções:
- Cite artigos específicos (ex: "Art. 18, §1º")
- Se não houver enquadramento claro, explique por quê
- Se a confiança for menor que 0.6, recomende consultar um advogado
- Responda em formato JSON

## Formato de resposta:
{{
  "is_cdc_case": true/false,
  "articles": [
    {{"number": "Art. X", "title": "...", "relevance": "..."}}
  ],
  "rights": ["Direito 1", "Direito 2"],
  "severity": "low|medium|high",
  "confidence": 0.X,
  "reasoning": "Explicação breve da análise"
}}
```

### 4.3 Estratégia de Encaminhamento

```
Você é um especialista em resolução de conflitos de consumo no Brasil.

Com base na análise jurídica abaixo, sugira a melhor estratégia de resolução
para o consumidor, priorizando a via mais rápida e menos custosa.

## Análise Jurídica:
{legal_analysis}

## Instruções:
- Sugira canais em ordem crescente de complexidade
- Para cada canal, inclua: nome, descrição prática, e link (quando disponível)
- Considere a gravidade do caso na priorização
- Se a gravidade for "high", sugira canais formais mais cedo

## Formato de resposta:
{{
  "channels": [
    {{"step": 1, "name": "...", "description": "...", "link": "..." ou null}}
  ],
  "estimated_resolution_time": "X dias/semanas",
  "tips": ["Dica prática 1", "Dica prática 2"]
}}
```

### 4.4 Formatação de Resposta

```
Você é o assistente Resolve Aí, especialista em direitos do consumidor.

Sua tarefa é formatar a resposta final para o consumidor de forma CLARA,
EMPÁTICA e ACIONÁVEL.

## Análise Jurídica:
{legal_analysis}

## Estratégia de Resolução:
{strategy}

## Instruções de formatação:
- Use linguagem simples (evite juridiquês)
- Comece com empatia ("Entendemos sua situação...")
- Apresente o enquadramento legal de forma acessível
- Liste os passos de resolução numerados
- Inclua links clicáveis
- Termine com uma mensagem de encorajamento
- Se a confiança da análise for baixa, adicione disclaimer
- Máximo de 400 palavras

## Tom:
- Empático mas profissional
- Claro e direto
- Encorajador ("Você TEM direitos neste caso")
```

---

## 5. Pipeline RAG — Especificação

### 5.1 Ingestão

| Etapa | Descrição | Output |
|-------|-----------|--------|
| 1. Download | Obter texto do CDC (planalto.gov.br ou PDF) | `data/cdc/cdc_raw.txt` |
| 2. Limpeza | Remover headers, footers, formatação HTML | `data/cdc/cdc_clean.txt` |
| 3. Chunking | Recursive splitter (800 tokens, 200 overlap) | Chunks com metadata |
| 4. Embedding | Gerar embeddings (text-embedding-004) | Vetores 768d |
| 5. Indexação | Inserir no ChromaDB | Collection `cdc_articles` |

### 5.2 Retrieval

| Parâmetro | Valor |
|-----------|:-----:|
| Top-K | 5 |
| Similarity metric | Cosine |
| Score threshold | 0.7 (descarta abaixo) |
| Metadata filter | Opcional (por capítulo) |

### 5.3 Fontes de Dados (MVP)

| Fonte | Formato | Prioridade |
|-------|:-------:|:----------:|
| CDC completo (Lei 8.078/1990) | TXT/PDF | 🔴 Essencial |
| Decreto 2.181/1997 (regulamenta o CDC) | TXT/PDF | 🟡 Desejável |

> 💡 **Dica de Sênior:** Não tente ingerir TUDO de uma vez. Comece com o CDC puro. Valide a qualidade. Depois adicione jurisprudência (Fase 2). Cada fonte nova precisa de re-avaliação da qualidade do RAG.

---

## 6. Casos de Teste (Golden Test Set)

Os 10 cenários abaixo formam o **golden test set** inicial para validar a qualidade:

| # | Cenário | Artigo Esperado | Severity |
|:-:|---------|:---------------:|:--------:|
| 1 | Produto com defeito dentro da garantia | Art. 18 | medium |
| 2 | Cobrança indevida no cartão de crédito | Art. 42 | medium |
| 3 | Propaganda enganosa (produto diferente do anunciado) | Art. 37 | medium |
| 4 | Serviço não prestado após pagamento | Art. 20 | high |
| 5 | Negativa de cancelamento de contrato | Art. 49 | medium |
| 6 | Descumprimento de oferta/promoção | Art. 35 | low |
| 7 | Produto perigoso causou dano à saúde | Art. 12 | high |
| 8 | Cláusula abusiva em contrato | Art. 51 | medium |
| 9 | Recusa de troca em compra online (7 dias) | Art. 49 | low |
| 10 | Negativação indevida (nome no SPC/Serasa) | Art. 43 | high |

Adicione mais 10 casos **negativos** (fora do CDC):
- Problema trabalhista (hora extra não paga)
- Problema tributário (IPTU cobrado errado)
- Conflito entre vizinhos
- Problema com plano de saúde (ANS, não CDC estritamente)
- Questão criminal (roubo de produto)

---

## 7. Métricas de Qualidade (Avaliação)

### MVP — Métricas Básicas

| Métrica | Target | Como medir |
|---------|:------:|-----------|
| **Precisão de artigos** | ≥ 80% | Golden test set: artigo correto nos top-3 |
| **Latência end-to-end** | < 15s | Timer no endpoint |
| **Uptime** | 99% | Health check periódico |

### Fase 2 — RAGAS (avançado)

| Métrica | Target | Descrição |
|---------|:------:|-----------|
| **Faithfulness** | ≥ 0.85 | Resposta é fiel ao contexto recuperado |
| **Context Precision** | ≥ 0.80 | Chunks relevantes estão no top-K |
| **Context Recall** | ≥ 0.75 | Contexto cobre a informação necessária |
| **Answer Relevancy** | ≥ 0.85 | Resposta é relevante à pergunta |

---

*Use este documento como especificação para cada componente. Risque os itens conforme forem implementados.*
