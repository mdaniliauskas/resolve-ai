"""
Orchestrator Agent — Resolve Aí

Classifies the user's intent to route to the correct pipeline path.
First node in the LangGraph workflow.
"""

import logging

from agents import llm_client

logger = logging.getLogger(__name__)

INTENT_PROMPT = """\
Você é um assistente especializado em Direito do Consumidor brasileiro.

Classifique a mensagem do usuário em UMA das categorias:
- "consumer_complaint": O usuário descreve um problema com produto ou serviço
- "general_question": O usuário tem uma dúvida sobre o CDC ou direitos do consumidor
- "greeting": O usuário está cumprimentando ou fazendo conversa casual
- "out_of_scope": A mensagem não tem relação com consumo ou direitos do consumidor

Mensagem do usuário: {user_message}

Responda APENAS com a categoria, sem explicações.
"""

VALID_INTENTS = {"consumer_complaint", "general_question", "greeting", "out_of_scope"}


def classify_intent(user_message: str) -> str:
    """Classify user message into one of the defined intent categories.

    Returns the intent string. Falls back to 'out_of_scope' if the LLM
    returns something unexpected.
    """
    prompt = INTENT_PROMPT.format(user_message=user_message)
    raw = llm_client.generate(prompt).strip().strip('"').lower()

    if raw in VALID_INTENTS:
        logger.info("Intent classified as '%s' for message: '%s...'", raw, user_message[:50])
        return raw

    logger.warning("LLM returned unexpected intent '%s', falling back to 'out_of_scope'", raw)
    return "out_of_scope"
