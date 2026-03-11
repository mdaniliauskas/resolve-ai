"""
RAGAS-inspired Evalutor — Resolve Aí

Uses an LLM (Gemini) to score RAG metrics: Faithfulness, Answer Relevance,
Context Precision, and Context Recall.

This simulates the 'ragas' library behavior using custom prompts for better
control and transparency during the interview demo.
"""

import json
import logging

from agents import llm_client

logger = logging.getLogger(__name__)

# --- Evaluation Prompts -------------------------------------------------------

FAITHFULNESS_PROMPT = """\
Dada a PERGUNTA, o CONTEXTO RECUPERADO e a RESPOSTA GERADA, avalie se a resposta é fiel ao contexto.
A resposta deve conter APENAS informações presentes no contexto ou deduções lógicas diretas dele.

PERGUNTA: {question}
CONTEXTO: {context}
RESPOSTA: {answer}

Instruções:
1. Identifique afirmações na resposta que NÃO estão no contexto.
2. Se houver alucinações (fatos inventados), a nota deve ser baixa.
3. Se a resposta for totalmente baseada no contexto, nota 1.0.

Responda SOMENTE um JSON:
{{"score": 0.0 a 1.0, "reasoning": "Breve explicação"}}
"""

RELEVANCE_PROMPT = """\
Avalie quão RELEVANTE é a RESPOSTA para a PERGUNTA do usuário.
Ignore se a informação é verídica ou não (isso é fé; avalie apenas se ela responde o que foi pedido).

PERGUNTA: {question}
RESPOSTA: {answer}

Responda SOMENTE um JSON:
{{"score": 0.0 a 1.0, "reasoning": "Breve explicação"}}
"""

CONTEXT_PRECISION_PROMPT = """\
Avalie a PRECISÃO do CONTEXTO RECUPERADO em relação à PERGUNTA.
Os trechos trazidos pelo RAG são realmente úteis para responder A ESTA pergunta específica?

PERGUNTA: {question}
CONTEXTO: {context}

Responda SOMENTE um JSON:
{{"score": 0.0 a 1.0, "reasoning": "Breve explicação"}}
"""

# --- Evaluator Class ----------------------------------------------------------

class RagasEvaluator:
    """Evaluates RAG performance using LLM-as-a-judge."""

    def __init__(self):
        self.results = []

    def evaluate_sample(self, question: str, context: str, answer: str) -> dict:
        """Run all metrics for a single Q&A pairs."""
        
        faithfulness = self._get_score(FAITHFULNESS_PROMPT, question=question, context=context, answer=answer)
        relevance = self._get_score(RELEVANCE_PROMPT, question=question, answer=answer)
        precision = self._get_score(CONTEXT_PRECISION_PROMPT, question=question, context=context)
        
        result = {
            "question": question,
            "metrics": {
                "faithfulness": faithfulness,
                "answer_relevance": relevance,
                "context_precision": precision
            }
        }
        return result

    def _get_score(self, prompt_template: str, **kwargs) -> dict:
        """Helper to call LLM and parse score."""
        prompt = prompt_template.format(**kwargs)
        try:
            raw = llm_client.generate(prompt)
            # Basic cleanup of markdown fences
            json_str = raw.strip()
            if json_str.startswith("```"):
                json_str = "\n".join(json_str.split("\n")[1:-1])
            
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error evaluating metric: {e}")
            return {"score": 0.0, "reasoning": f"Erro: {e}"}

def run_full_evaluation():
    """Run RAGAS evaluation against a sample of the Golden Test Set."""

    from agents.workflow import run_chat
    from evaluation.golden_test_set import GOLDEN_CASES

    evaluator = RagasEvaluator()
    samples = GOLDEN_CASES[:3] # Evaluation can be slow/expensive, start with top 3
    
    print("\n" + "="*72)
    print("  RAGAS EVALUATION (Simulated via Gemini)")
    print("="*72)

    all_results = []
    
    for case in samples:
        print(f"\nAvaliando Caso {case.id}: {case.query[:50]}...")
        
        # 1. Run the system
        result = run_chat(case.query)
        answer = result["response"]
        context_texts = [f"[{c.source_type.upper()} {c.reference}] {c.text}" for c in result["rag_chunks"]]
        context = "\n---\n".join(context_texts)
        
        # 2. Score
        score_result = evaluator.evaluate_sample(case.query, context, answer)
        all_results.append(score_result)
        
        # 3. Print
        m = score_result["metrics"]
        print(f"  - Faithfulness: {m['faithfulness']['score']:.2f} | {m['faithfulness']['reasoning']}")
        print(f"  - Relevance:     {m['answer_relevance']['score']:.2f} | {m['answer_relevance']['reasoning']}")
        print(f"  - Precision:     {m['context_precision']['score']:.2f} | {m['context_precision']['reasoning']}")

    # Calculate Totals
    avg_f = sum(r["metrics"]["faithfulness"]["score"] for r in all_results) / len(all_results)
    avg_r = sum(r["metrics"]["answer_relevance"]["score"] for r in all_results) / len(all_results)
    
    print("\n" + "-"*72)
    print(f"  Média Faithfulness: {avg_f:.2f}")
    print(f"  Média Relevance:     {avg_r:.2f}")
    print("="*72 + "\n")

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    run_full_evaluation()
