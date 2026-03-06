# Guia de Prompts para Desenvolvimento Assistido por IA 🤖

> Templates de prompts otimizados para usar com IA no desenvolvimento de cada componente do Resolve Aí.

---

## Filosofia: Prompts como Especificações

A qualidade do código gerado por IA é diretamente proporcional à qualidade do prompt. Trate cada prompt como uma **micro-especificação**.

**Estrutura de um bom prompt para geração de código:**
```
1. CONTEXTO: O que é o projeto, qual framework/lib usar
2. TAREFA: O que precisa ser implementado
3. SPEC: Inputs, outputs, comportamento esperado
4. RESTRIÇÕES: O que NÃO fazer, limites, padrões a seguir
5. FORMATO: Como quer a resposta (código, explicação, ambos)
```

---

## 1. Prompts para o Pipeline RAG

### 1.1 Ingestão do CDC

```markdown
## Contexto
Estou construindo um pipeline RAG para o Resolve Aí, um chatbot de defesa do consumidor.
Estou usando Python, LlamaIndex e ChromaDB.

## Tarefa
Implemente um script de ingestão que:
1. Leia o texto do CDC (Lei 8.078/1990) de um arquivo TXT
2. Faça chunking com RecursiveCharacterTextSplitter (800 tokens, 200 overlap)
3. Adicione metadata a cada chunk: {titulo, capitulo, secao, artigo_numero}
4. Gere embeddings e indexe no ChromaDB

## Restrições
- Use `chromadb.PersistentClient` (não servidor)
- Use `text-embedding-004` do Gemini para embeddings
- Faça fallback para `all-MiniLM-L6-v2` se a chave Gemini não estiver disponível
- O script deve ser idempotente (pode rodar mais de uma vez sem duplicar dados)

## Formato
Código Python completo com docstrings e comments explicativos.
Separe em funções: load_document(), chunk_document(), create_embeddings(), index_chunks()
```

### 1.2 Retrieval

```markdown
## Contexto
Pipeline RAG do Resolve Aí. ChromaDB já tem o CDC indexado.

## Tarefa
Implemente a função de retrieval que:
1. Recebe uma query do usuário (em português)
2. Gera o embedding da query
3. Faz similarity search no ChromaDB (top_k=5, threshold=0.7)
4. Retorna os chunks com score e metadata

## Restrições
- Retorne um list[RetrievedChunk] usando Pydantic model
- Descarte resultados com score < 0.7
- Logue os scores para debug
- Async-ready (async def)
```

---

## 2. Prompts para Agentes (LangGraph)

### 2.1 Estrutura do Grafo

```markdown
## Contexto
Resolve Aí — chatbot multi-agentes com LangGraph.
State schema:

```python
class ResolveAiState(TypedDict):
    user_message: str
    intent: str
    is_cdc_case: bool
    legal_analysis: Optional[dict]
    rag_context: Optional[list]
    strategy: Optional[dict]
    final_response: str
```

## Tarefa
Implemente o StateGraph do LangGraph com:
- 4 nós: orchestrator, legal_analysis, strategy, response
- Conditional edge após orchestrator: cdc_case → legal_analysis, out_of_scope → response
- Edges lineares: legal_analysis → strategy → response

## Restrições
- Cada nó é uma função async que recebe e retorna ResolveAiState
- Use START e END do LangGraph
- Não use subgraphs, human-in-the-loop ou paralelismo (MVP simples)
- Inclua type hints completos
```

### 2.2 Implementar um Agente Específico

```markdown
## Contexto
Resolve Aí — estou implementando o Agente de Análise Jurídica.
Ele recebe o state do LangGraph com user_message e rag_context.

## Tarefa
Implemente o nó `legal_analysis_node` que:
1. Monta o prompt com user_message + rag_context
2. Chama o LLM (Gemini via google-generativeai)
3. Parseia a resposta JSON do LLM
4. Atualiza o state com legal_analysis

## Prompt do agente
[Cole o prompt template do MVP_SPEC.md aqui]

## Restrições
- Use `google.generativeai` para chamar o Gemini
- Parse a resposta como JSON (trate o caso de JSON inválido)
- Se o LLM não retornar JSON válido, faça retry até 2x
- Logue o prompt enviado e a resposta recebida (nível DEBUG)
- Use Pydantic para validar o output
```

---

## 3. Prompts para a API (FastAPI)

### 3.1 Scaffold da API

```markdown
## Contexto
Backend do Resolve Aí em FastAPI.

## Tarefa
Crie o arquivo api/main.py com:
1. App FastAPI com título "Resolve Aí API" e versão "0.1.0"
2. CORS middleware para http://localhost:3000
3. POST /api/chat que recebe {message: str} e retorna a resposta
4. GET /api/health
5. Error handling global (retorna JSON em qualquer erro)

## Restrições
- Use Pydantic v2 para request/response models
- Async handlers
- Importe o grafo LangGraph do módulo agents
- Response model com: response, articles, severity, sources, metadata
- Não inclua autenticação (MVP)
```

---

## 4. Prompts para Testes

### 4.1 Gerar Testes de um Módulo

```markdown
## Contexto
Resolve Aí — testo o módulo de análise jurídica.

## Código do módulo
[Cole o código aqui]

## Tarefa
Gere testes com pytest para este módulo:
1. Testes de happy path (caso CDC válido)
2. Testes de edge cases (input vazio, fora do CDC, JSON inválido)
3. Testes de propriedade (resposta contém artigos, severity é válido, etc.)

## Restrições
- Use pytest + pytest-asyncio
- Mocke as chamadas ao LLM (não chame a API real nos testes unitários)
- Use fixtures para dados de teste reutilizáveis
- Cada teste deve ter docstring explicando o cenário
```

### 4.2 Testes do RAG (Retrieval)

```markdown
## Contexto
Testo o retrieval do pipeline RAG do Resolve Aí.

## Tarefa
Gere testes que verifiquem:
1. Query sobre "produto defeituoso" retorna chunks com Art. 18
2. Query sobre "cobrança indevida" retorna chunks com Art. 42
3. Query fora do CDC ("hora extra no trabalho") retorna poucos/nenhum resultado
4. Score dos chunks relevantes é > 0.7

## Restrições
- Use um ChromaDB em memória para testes (chromadb.Client())
- Pré-indexe um subset do CDC (10 artigos) como fixture
- Não mocke o ChromaDB — é teste de integração
```

---

## 5. Prompts para Debug

### 5.1 Template de Debug

```markdown
## Problema
[Descreva o que está acontecendo vs. o que deveria acontecer]

## Stack Trace
```
[Cole o stack trace completo]
```

## Código Relevante
```python
[Cole o código onde o erro ocorre]
```

## O que já tentei
1. [O que você já tentou]

## Ambiente
- Python [versão]
- [lib relevante] [versão]
- OS: Windows
```

### 5.2 Debug de RAG (respostas ruins)

```markdown
## Problema
O RAG está retornando chunks irrelevantes para a query "[query]".

## Chunks retornados
1. Score: X.XX | "[texto do chunk]"
2. Score: X.XX | "[texto do chunk]"

## Chunk esperado
"[texto do chunk que deveria ter sido retornado]"

## Configuração atual
- Chunk size: [X] tokens
- Overlap: [X] tokens
- Embedding model: [modelo]
- Top-K: [X]
- Distance metric: [métrica]

## Pergunta
Por que os chunks irrelevantes estão com score alto?
O que devo ajustar: chunking, embedding, ou query?
```

---

## 6. Prompts para Documentação

### 6.1 Gerar Docstrings

```markdown
## Tarefa
Adicione docstrings Google-style a todas as funções deste módulo.
Inclua: descrição, Args, Returns, Raises, e exemplo de uso.

## Código
[Cole o código]
```

### 6.2 Gerar README de um Componente

```markdown
## Contexto
Componente: [nome] do projeto Resolve Aí

## Tarefa
Gere um README.md para este componente com:
1. O que é e para que serve
2. Como usar (exemplo de código)
3. Configuração necessária
4. Testes disponíveis

## Formato
Markdown com code blocks e tabelas onde relevante.
```

---

## 7. Prompts para Revisão de Código

### 7.1 Code Review

```markdown
## Contexto
Projeto Resolve Aí — Python, FastAPI, LangGraph.

## Tarefa
Faça uma code review deste código focando em:
1. Bugs ou erros lógicos
2. Segurança (SQL injection, prompt injection, secrets expostos)
3. Performance (chamadas desnecessárias, N+1, bloqueio de event loop)
4. Legibilidade e padrões (PEP 8, naming, complexidade)
5. Testes ausentes

## Código
[Cole o código]

## Formato
Liste os issues por severidade: 🔴 Critical, 🟡 Warn, 🟢 Sugestão
```

---

## 8. Meta-Prompts (Prompts sobre Prompts)

### 8.1 Melhorar um Prompt de Agente

```markdown
## Contexto
Estou otimizando o prompt do Agente de Análise Jurídica do Resolve Aí.

## Prompt atual
[Cole o prompt]

## Problemas observados
- [Ex: O modelo às vezes retorna JSON malformado]
- [Ex: Confiança é sempre 0.9, nunca varia]

## Tarefa
Melhore este prompt para:
1. Garantir output JSON válido (use delimitadores explícitos)
2. Calibrar melhor a confiança
3. Manter o prompt abaixo de 500 tokens

## Formato
Retorne o prompt melhorado + explicação das mudanças feitas.
```

---

## Dicas Gerais para Prompts Melhores

| Dica | Exemplo |
|------|---------|
| **Seja específico sobre libs** | ❌ "Use um vector store" → ✅ "Use ChromaDB com PersistentClient" |
| **Cole o code existente** | A IA integra melhor quando vê o contexto real |
| **Diga o que NÃO fazer** | "Não use decorators complexos, mantenha simples" |
| **Peça explicações** | "Explique cada decisão de design no código" |
| **Itere** | O primeiro prompt gera 70%. Refine com follow-ups |
| **Valide sempre** | Execute o código gerado. IA erra nomes de funções e APIs |

---

*Use estes templates como ponto de partida. Adapte conforme seu estilo e necessidade.*
