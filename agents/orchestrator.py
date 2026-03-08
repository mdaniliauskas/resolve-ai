"""
Orchestrator Agent — Resolve Aí

Classifies the user's intent to route to the correct pipeline path.
First node in the LangGraph workflow.
"""

import logging

from agents import llm_client

logger = logging.getLogger(__name__)

INTENT_PROMPT = """\
Você é um classificador de intenções RESTrito e INFLEXÍVEL para um assistente de Direito do Consumidor brasileiro (CDC).

CLASSIFIQUE a mensagem do usuário em estritamente UMA das seguintes categorias:
- "consumer_complaint": O usuário descreve um problema ou conflito com produto, serviço, loja, empresa ou contrato.
- "general_question": O usuário tem uma dúvida teórica sobre o CDC, devolução, garantia ou direitos do consumidor.
- "greeting": O usuário está apenas dizendo "olá", "bom dia", "como funciona", ou iniciando conversa.
- "out_of_scope": QUALQUER outro assunto. Exemplos: programação, receitas, política, matemática, contar piadas, criar histórias, traduzir textos ou perguntas médicas/legais fora do CDC.

MENSAGEM DO USUÁRIO: {user_message}

**REGRA DE OURO:** Se houver 1% de dúvida se o assunto é sobre Direito do Consumidor, classifique imediatamente como "out_of_scope". Proteja os tokens da aplicação.

Responda APENAS com a categoria (string exata), sem aspas ou explicações adicionais.
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
