# Guia de Desenvolvimento — Resolve Aí 🧑‍💻

> Filosofia de desenvolvimento, dicas de sênior, padrões de código e como usar IA como copiloto eficiente.

---

## 1. Filosofia de Desenvolvimento

### 1.1 Spec-Driven Development

**O que é:** Antes de escrever código, escreva a especificação. Isso inclui: o que o componente faz, quais inputs recebe, quais outputs retorna, e como se comporta em edge cases.

**Por que importa:**
- Reduz retrabalho (você pensa antes de fazer)
- Documenta antes de esquecer
- Permite que a IA gere código muito melhor (especificação = prompt)

**Na prática:**
```markdown
# Spec: Agente de Análise Jurídica

## Input
- user_message: str — relato do consumidor
- rag_context: list[str] — chunks recuperados do CDC

## Output
- articles: list[str] — artigos do CDC aplicáveis
- rights: list[str] — direitos do consumidor neste caso
- severity: "low" | "medium" | "high"
- confidence: float (0-1)

## Comportamento
- Se não encontrar artigos aplicáveis, retorna lista vazia + severity "low"
- Se a confiança for < 0.5, adiciona disclaimer na resposta
- Tempo máximo de processamento: 10s
```

> 💡 **Dica de Sênior:** Essa spec se torna o docstring da sua classe, o contrato da API, e o prompt para pedir à IA que gere a implementação. Um documento, três usos.

---

### 1.2 Iterativo, Não Perfeito

**Regra de ouro para o MVP:** Faça funcionar → Faça funcionar direito → Faça rápido.

```
Sprint 1: Chat que responde qualquer coisa (fim a fim funcionando)
Sprint 2: RAG do CDC conectado (respostas fundamentadas)
Sprint 3: Agentes separados (orquestração real)
Sprint 4: Qualidade (avaliação, testes, polimento)
```

> ⚠️ **Anti-pattern:** Ficar 2 semanas perfecionando o pipeline RAG antes de ter um chat que funciona. Sempre feche o loop end-to-end primeiro, mesmo que a qualidade seja ruim.

---

### 1.3 Test-First (onde faz sentido)

Não precisa ser TDD religioso, mas **para os agentes**, escreva testes antes:

```python
# tests/unit/test_legal_analysis.py

def test_identifies_defective_product():
    """Caso clássico: produto com defeito dentro da garantia."""
    result = analyze("Comprei um celular há 15 dias e a tela parou de funcionar")
    assert "Art. 18" in result["articles"]
    assert result["severity"] in ["medium", "high"]

def test_out_of_scope():
    """Caso fora do CDC: relação trabalhista."""
    result = analyze("Meu chefe não pagou meu salário")
    assert result["articles"] == []
    assert result["is_cdc_case"] == False
```

> 💡 **Dica de Sênior:** Testes para LLMs são um tema quente. Você não vai testar output exato (LLMs são não-determinísticos). Teste **propriedades**: "a resposta contém artigo 18?", "o severity é high para caso grave?", "a resposta tem menos de 500 tokens?". Isso se chama **property-based testing** para LLMs.

---

## 2. Padrões de Código

### 2.1 Estrutura de um Módulo

```python
"""
Agente de Análise Jurídica — Resolve Aí

Responsabilidade: Consultar o RAG do CDC e determinar se o caso
do consumidor se enquadra no Código de Defesa do Consumidor.

Referências:
- CDC: Lei nº 8.078/1990
- ARCHITECTURE.md: Seção 5.2
"""

from typing import Optional
from pydantic import BaseModel

# === Models ===

class LegalAnalysisInput(BaseModel):
    user_message: str
    rag_context: list[str]

class LegalAnalysisOutput(BaseModel):
    articles: list[str]
    rights: list[str]
    severity: str  # "low" | "medium" | "high"
    confidence: float

# === Core Logic ===

async def analyze(input: LegalAnalysisInput) -> LegalAnalysisOutput:
    """Análise jurídica com base no CDC via RAG."""
    ...

# === Helpers (private) ===

def _extract_articles(text: str) -> list[str]:
    """Extrai referências a artigos do CDC do texto."""
    ...
```

**Princípios:**
- Docstring no topo do módulo com **responsabilidade** clara
- **Pydantic** para inputs/outputs (validação + serialização + documentação)
- Funções `async` para I/O (chamadas à API, RAG)
- Helpers privados com `_` prefix
- Um módulo = uma responsabilidade

### 2.2 Naming Conventions

| Elemento | Convenção | Exemplo |
|----------|-----------|---------|
| Arquivos | snake_case | `legal_analysis.py` |
| Classes | PascalCase | `LegalAnalysisAgent` |
| Funções | snake_case | `analyze_case()` |
| Constantes | UPPER_CASE | `MAX_RETRY_COUNT` |
| Variáveis de ambiente | UPPER_CASE | `GEMINI_API_KEY` |

### 2.3 Tratamento de Erros

```python
# ❌ Não faça:
try:
    result = await llm.generate(prompt)
except:
    pass

# ✅ Faça:
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=10),
    reraise=True
)
async def generate_with_retry(prompt: str) -> str:
    """Chama o LLM com retry exponential."""
    try:
        result = await llm.generate(prompt)
        return result
    except RateLimitError as e:
        logger.warning(f"Rate limit atingido, tentando novamente: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado na geração: {e}")
        raise LLMGenerationError(f"Falha ao gerar resposta: {e}") from e
```

> 💡 **Dica de Sênior:** APIs de LLM falham. Sempre. Use a lib `tenacity` para retry com backoff exponencial. Rate limits do Gemini são generosos, mas em produção você vai bater neles.

---

## 3. Dicas de Sênior por Componente

### 3.1 RAG — Os Erros que Todo Mundo Comete

| Anti-Pattern | O que acontece | Solução |
|-------------|----------------|---------|
| Chunks grandes demais (>1500 tokens) | Contexto irrelevante dilui a resposta | Use 500-800 tokens com overlap de 200 |
| Sem metadata nos chunks | Impossível filtrar por artigo/capítulo | Adicione artigo, capítulo, seção como metadata |
| Retrieval sem re-ranking | Top-K retorna chunks pouco relevantes | Use cross-encoder ou Reciprocal Rank Fusion |
| Embedding do query igual ao do documento | Query curta vs. documento longo = mismatch | Use HyDE (Hypothetical Document Embedding) |
| Não testar o retrieval separado | Não sabe se o problema é no retrieval ou na geração | Meça **Context Precision** e **Context Recall** isoladamente |

#### Como debugar seu RAG:

```python
# 1. Veja o que o retrieval está retornando
results = retriever.retrieve("produto com defeito na garantia")
for r in results:
    print(f"Score: {r.score:.3f} | Chunk: {r.text[:100]}...")

# 2. Se os chunks errados estão voltando:
#    → Problema no chunking ou no embedding
#    → Tente chunks menores ou outro modelo de embedding

# 3. Se os chunks certos voltam mas a resposta é ruim:
#    → Problema no prompt do agente
#    → Adicione few-shot examples no prompt
```

> 💡 **Dica de Sênior:** Crie um **golden test set**: 20 perguntas com a resposta esperada e os artigos corretos. Rode o RAG nesse set e meça a precisão. Esse é seu benchmark. Sem ele, você está otimizando no escuro.

---

### 3.2 Agentes (LangGraph) — Complexidade Sob Controle

**A tentação:** Criar um grafo hiper-complexo com 10 nós e condições em todo lugar.

**A realidade:** Para o MVP, seu grafo tem **4 nós e 2 condições**. Mantenha assim.

```python
# ✅ MVP — Simples e funcional
graph = StateGraph(ResolveAiState)
graph.add_node("orchestrator", orchestrator_node)
graph.add_node("legal_analysis", legal_analysis_node)
graph.add_node("strategy", strategy_node)
graph.add_node("response", response_node)

graph.add_edge(START, "orchestrator")
graph.add_conditional_edges(
    "orchestrator",
    route_by_intent,
    {
        "cdc_case": "legal_analysis",
        "out_of_scope": "response",  # resposta direta
    }
)
graph.add_edge("legal_analysis", "strategy")
graph.add_edge("strategy", "response")
graph.add_edge("response", END)
```

**Evite no MVP:**
- ❌ Loops de auto-correção ("o agente revisa a própria resposta")
- ❌ Agentes que chamam outros agentes recursivamente
- ❌ Estado global mutável entre agentes
- ❌ Paralelismo de agentes (LangGraph suporta, mas complica debug)

> 💡 **Dica de Sênior:** Cada nó do LangGraph deve ser uma **função pura**: recebe o state, retorna o state modificado. Sem side effects, sem estado global, sem mutações. Isso facilita testes, debug e rastreabilidade.

---

### 3.3 API (FastAPI) — O Mínimo Necessário

```python
# api/main.py — MVP
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Resolve Aí API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    articles: list[str] = []
    severity: str = ""
    sources: list[str] = []

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Chama o grafo LangGraph
    result = await graph.ainvoke({"user_message": request.message})
    return ChatResponse(
        response=result["final_response"],
        articles=result.get("legal_analysis", {}).get("articles", []),
        severity=result.get("legal_analysis", {}).get("severity", ""),
        sources=[c.metadata.get("source", "") for c in result.get("rag_context", [])],
    )

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

> 💡 **Dica de Sênior:** Use `response_model` no FastAPI. Ele gera o schema OpenAPI automaticamente, valida a resposta, e filtra campos extras. Menos código, mais garantia.

---

### 3.4 Frontend — Pragmatismo no MVP

**Para o MVP, você precisa de:**
- ✅ Um campo de texto para digitar
- ✅ Um botão de enviar
- ✅ Uma área de resposta (com Markdown renderizado)
- ✅ Indicador de carregamento
- ✅ Disclaimer legal

**Você NÃO precisa de:**
- ❌ Sistema de autenticação
- ❌ Histórico de conversas persistido
- ❌ Temas dark/light
- ❌ Animações elaboradas
- ❌ PWA / Service Worker

> 💡 **Dica de Sênior:** Se o backend funciona bem, qualquer frontend simples resolve. Se o backend não funciona, nenhum frontend bonito salva. **Backend primeiro, frontend depois.**

---

## 4. Usando IA como Copiloto — Sem Perder a Autonomia

### 4.1 A Regra dos 3 Passos

Antes de pedir à IA para gerar código:

1. **Entenda o que você quer** — Escreva a spec (mesmo que informal)
2. **Peça para a IA gerar** — Usando prompts específicos (ver [PROMPTS_GUIDE.md](./PROMPTS_GUIDE.md))
3. **Revise criticamente** — Entenda cada linha. Se não entendeu, pergunte "por que fez assim?"

### 4.2 O que Pedir à IA

| Cenário | Eficiência da IA | Exemplo |
|---------|:-----------------:|---------|
| Boilerplate / setup | ⭐⭐⭐⭐⭐ | "Gere o scaffold do FastAPI com CORS e health check" |
| Implementação com spec clara | ⭐⭐⭐⭐ | "Implemente esta spec: [cola a spec]" |
| Debug com stack trace | ⭐⭐⭐⭐ | "Este erro ocorre quando X. Stack trace: [...]" |
| Testes baseados em spec | ⭐⭐⭐⭐ | "Gere testes para esta função: [cola a função]" |
| Decisões de arquitetura | ⭐⭐ | Melhor pesquisar e decidir você |
| Prompt engineering | ⭐⭐⭐ | Bom para iterar, mas você precisa avaliar a qualidade |
| Otimização de performance | ⭐⭐ | Precisa de profiling real, IA costuma otimizar prematuramente |

### 4.3 Aprendendo Enquanto Usa IA

**Template para aprender com cada geração:**

```
IA gerou: [código]

Minha checklist:
□ Entendi o que cada função faz?
□ Entendi por que usou essa lib/pattern?
□ Conseguiria explicar para alguém?
□ Tem testes para validar?
□ Há edge cases não cobertos?
```

> 💡 **Dica de Sênior:** O maior risco do dev assistido por IA é criar código que você não entende. Mantenha uma regra: **se não consegue EXPLICAR o que o código faz, não comite.** A IA é uma ferramenta, não um substituto para entendimento.

### 4.4 O Anti-Pattern do "Aceitar Tudo"

```
❌ Fluxo ruim:
   Perguntar → Copiar → Colar → Próxima pergunta

✅ Fluxo bom:
   Perguntar → Ler → Entender → Adaptar → Testar → Próxima pergunta
```

---

## 5. Checklist de Qualidade (Antes de Cada Commit)

### Código
- [ ] Passa no `ruff check .` (linting) sem warnings
- [ ] Passa no `mypy .` (type checking) sem erros
- [ ] Funções têm docstrings descritivas
- [ ] Sem secrets hardcoded (use `.env`)
- [ ] Sem `print()` — use `logging`

### Testes
- [ ] Testes existem para a funcionalidade nova
- [ ] `pytest` passa com 0 falhas
- [ ] Edge cases considerados (input vazio, resposta longa, timeout)

### Git
- [ ] Commit message descritiva: `feat(rag): add CDC chunking pipeline`
- [ ] Arquivos desnecessários no `.gitignore` (`.env`, `__pycache__`, `data/chroma_db/`)
- [ ] Branch separada para features grandes

### Documentação
- [ ] README atualizado se mudou a API ou o setup
- [ ] Specs atualizadas se mudou o comportamento

---

## 6. Padrões Git — Conventional Commits

```
feat(component): descrição curta
fix(component): descrição curta
docs(component): descrição curta
test(component): descrição curta
refactor(component): descrição curta
chore(component): descrição curta

Exemplos:
feat(rag): implement CDC text chunking pipeline
feat(agents): add legal analysis agent with LangGraph
fix(api): handle empty message in chat endpoint
docs(readme): add architecture diagram
test(agents): add property tests for orchestrator
```

---

## 7. Ordem de Implementação Recomendada

```
1. API esqueleto (FastAPI + health check)         ──→ fim a fim
2. RAG: ingestão do CDC (chunking + embedding)     ──→ dados prontos
3. RAG: retrieval básico (similarity search)       ──→ busca funcional
4. Agente de Análise Jurídica (prompt + RAG)       ──→ primeiro agente
5. Agente Orquestrador (roteamento simples)        ──→ coordenação
6. Agente de Resposta (formatação)                 ──→ output legível
7. Frontend chat (minimal)                         ──→ interface
8. Integrar tudo via LangGraph                     ──→ MVP completo
9. Agente de Estratégia                            ──→ plano de ação
10. Avaliação com RAGAS                            ──→ qualidade medida
```

> 💡 **Dica de Sênior:** Essa ordem não é aleatória. Ela garante que a cada passo você tem algo testável e demonstrável. O item 1-3 sozinho já é um demo: "faço uma pergunta sobre o CDC e recebo os chunks relevantes". O item 4-6 adiciona inteligência. O item 7-8 fecha o loop. O item 9-10 adiciona profundidade.

---

*Próximo passo: leia [PROMPTS_GUIDE.md](./PROMPTS_GUIDE.md) para templates de prompts específicos por componente.*
