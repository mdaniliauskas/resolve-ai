"""
Agent Workflow — Resolve Aí

LangGraph StateGraph that wires all agents into an end-to-end pipeline.
Entry points:
  run_chat(message) → ChatResult          (blocking, for tests)
  stream_chat(message, queue) → None      (SSE-friendly, puts events in queue)
"""

import logging
import queue as queue_module
import threading
import time
from typing import Generator, TypedDict

from langgraph.graph import END, StateGraph

from agents.legal_analysis import LegalAnalysisResult, analyze_case
from agents.orchestrator import classify_intent
from agents.response import format_greeting, format_out_of_scope, format_response
from agents.strategy import StrategyResult, plan_strategy
from rag.retrieval import RetrievedChunk, retrieve

logger = logging.getLogger(__name__)


# --- State Schema -------------------------------------------------------------


class ResolveAiState(TypedDict, total=False):
    """Shared state passed through the LangGraph workflow."""

    # Input
    user_message: str

    # Orchestrator
    intent: str
    is_cdc_case: bool

    # Legal Analysis
    rag_chunks: list[RetrievedChunk]
    legal_analysis: LegalAnalysisResult | None

    # Strategy
    strategy: StrategyResult | None

    # Response
    final_response: str


# --- Result Model -------------------------------------------------------------


class ChatResult(TypedDict):
    """Final output returned to the API layer."""

    response: str
    analysis: LegalAnalysisResult | None
    strategy: StrategyResult | None
    rag_chunks: list[RetrievedChunk]
    sources: list[str]
    metadata: dict


# --- Graph Nodes --------------------------------------------------------------


def orchestrator_node(state: ResolveAiState) -> dict:
    """Classify the user's intent and decide the pipeline path."""
    intent = classify_intent(state["user_message"])
    is_cdc = intent in ("consumer_complaint", "general_question")
    return {"intent": intent, "is_cdc_case": is_cdc}


def retrieval_node(state: ResolveAiState) -> dict:
    """Retrieve relevant CDC chunks via RAG."""
    chunks = retrieve(state["user_message"])
    return {"rag_chunks": chunks}


def legal_analysis_node(state: ResolveAiState) -> dict:
    """Analyze the case against CDC articles."""
    analysis = analyze_case(state["user_message"], state.get("rag_chunks", []))
    return {"legal_analysis": analysis}


def strategy_node(state: ResolveAiState) -> dict:
    """Plan resoltion channels based on the legal analysis."""
    analysis = state.get("legal_analysis") or LegalAnalysisResult()
    strategy = plan_strategy(analysis)
    return {"strategy": strategy}


def response_node(state: ResolveAiState) -> dict:
    """Format the final consumer-facing response."""
    intent = state.get("intent", "out_of_scope")
    analysis = state.get("legal_analysis")
    strategy = state.get("strategy")

    if intent == "greeting":
        text = format_greeting()
    elif not state.get("is_cdc_case"):
        text = format_out_of_scope()
    elif analysis and strategy:
        text = format_response(state["user_message"], analysis, strategy)
    else:
        text = format_out_of_scope()

    return {"final_response": text}


# --- Routing ------------------------------------------------------------------


def route_after_orchestrator(state: ResolveAiState) -> str:
    """Decide which path to take after intent classification."""
    if state.get("is_cdc_case"):
        return "retrieval"
    return "response"


# --- Build Graph --------------------------------------------------------------


def _build_graph() -> StateGraph:
    """Construct the LangGraph workflow (called once)."""
    graph = StateGraph(ResolveAiState)

    # Add nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("legal_analysis", legal_analysis_node)
    graph.add_node("strategy", strategy_node)
    graph.add_node("response", response_node)

    # Set entry point
    graph.set_entry_point("orchestrator")

    # Conditional routing after orchestrator
    graph.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {"retrieval": "retrieval", "response": "response"},
    )

    # Linear flow for CDC cases: retrieval → legal_analysis → strategy → response
    graph.add_edge("retrieval", "legal_analysis")
    graph.add_edge("legal_analysis", "strategy")
    graph.add_edge("strategy", "response")

    # End after response
    graph.add_edge("response", END)

    return graph


# Compile once at module level
_compiled_graph = _build_graph().compile()


# --- Stage messages shown to the user while the pipeline runs ----------------

_STAGE_MESSAGES: dict[str, str] = {
    "orchestrator": "Entendendo sua situação...",
    "retrieval": "Consultando o Código de Defesa do Consumidor...",
    "legal_analysis": "Analisando seus direitos...",
    "strategy": "Montando o plano de ação...",
    "response": "Preparando sua resposta...",
}


# --- Shared result builder ----------------------------------------------------


def _build_result(final_state: dict, elapsed_ms: float) -> ChatResult:
    """Build a ChatResult from a completed LangGraph final state."""
    analysis = final_state.get("legal_analysis")
    strategy = final_state.get("strategy")
    rag_chunks = final_state.get("rag_chunks", [])

    sources = []
    for chunk in rag_chunks:
        source_name = "CDC" if chunk.source_type == "cdc" else "STJ"
        label = f"{source_name} {chunk.reference}" if chunk.reference else source_name
        if chunk.source_type == "cdc":
            if chunk.secao:
                label += f" - {chunk.secao}"
            elif chunk.capitulo:
                label += f" - {chunk.capitulo}"
        sources.append(label)

    return ChatResult(
        response=final_state.get("final_response", ""),
        analysis=analysis,
        strategy=strategy,
        rag_chunks=rag_chunks,
        sources=sources,
        metadata={
            "intent": final_state.get("intent", ""),
            "latency_ms": round(elapsed_ms),
        },
    )


# --- Public API ---------------------------------------------------------------


def run_chat(message: str) -> ChatResult:
    """Run the full agent pipeline for a user message (blocking)."""
    start = time.perf_counter()
    initial_state: ResolveAiState = {"user_message": message}
    final_state = _compiled_graph.invoke(initial_state)
    elapsed_ms = (time.perf_counter() - start) * 1000

    result = _build_result(dict(final_state), elapsed_ms)
    logger.info(
        "Chat pipeline completed in %.0fms (intent=%s, sources=%d)",
        elapsed_ms,
        final_state.get("intent"),
        len(result["sources"]),
    )
    return result


def _run_pipeline_into_queue(message: str, q: queue_module.Queue) -> None:
    """Run LangGraph pipeline in a thread, pushing SSE events into queue."""
    start = time.perf_counter()
    initial_state: ResolveAiState = {"user_message": message}
    accumulated: dict = {}

    try:
        for event in _compiled_graph.stream(initial_state, stream_mode="updates"):
            node_name = next(iter(event))
            accumulated.update(event[node_name])
            stage = _STAGE_MESSAGES.get(node_name)
            if stage:
                q.put({"type": "stage", "stage": stage})

        elapsed_ms = (time.perf_counter() - start) * 1000
        result = _build_result(accumulated, elapsed_ms)

        # Convert dataclasses to dicts for JSON serialisation
        import dataclasses

        def _to_dict(obj):  # type: ignore[return]
            if dataclasses.is_dataclass(obj):
                return dataclasses.asdict(obj)
            if isinstance(obj, list):
                return [_to_dict(i) for i in obj]
            return obj

        q.put({
            "type": "done",
            "data": {
                "response": result["response"],
                "analysis": _to_dict(result["analysis"]),
                "strategy": _to_dict(result["strategy"]),
                "sources": result["sources"],
                "metadata": result["metadata"],
            },
        })
    except Exception:
        logger.exception("Streaming pipeline failed")
        q.put({"type": "error", "message": "Ocorreu um erro. Tente novamente."})
    finally:
        q.put(None)  # sentinel — stream is done


def stream_chat(message: str) -> Generator[dict, None, None]:
    """Yield SSE event dicts as the pipeline progresses.

    Each yielded dict has a 'type' key:
      - {"type": "stage", "stage": "<human-readable step>"}
      - {"type": "done",  "data": <ChatResult as dict>}
      - {"type": "error", "message": "<error text>"}
    """
    q: queue_module.Queue = queue_module.Queue()
    thread = threading.Thread(
        target=_run_pipeline_into_queue,
        args=(message, q),
        daemon=True,
    )
    thread.start()

    while True:
        item = q.get()
        if item is None:
            break
        yield item
