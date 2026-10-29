import logging
from google import genai
from google.genai import types

from config.settings import settings
from core.erros import FalhaIA

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

MODELO_GEMINI = "gemini-2.5-flash"


def _linhas_da_resposta(response) -> list:
    return [
        linha.strip()
        for linha in (response.text or "").split("\n")
        if linha.strip()
    ]


def gerar_passos_tarefa(titulo_tarefa: str) -> list:
    """Usa o Gemini para quebrar uma tarefa macro em micro-ações sequenciais."""

    if not client:
        raise FalhaIA("GEMINI_API_KEY não configurada. Configure sua chave de API.")

    prompt = (
        f"Quebre a seguinte tarefa em exatamente 3 ou 4 passos sequenciais, "
        f"curtos e fáceis de focar: '{titulo_tarefa}'. "
        f"Escreva apenas os passos, um por linha, sem introduções ou numeração manual."
    )

    system_instruction = (
        "Você é um especialista em produtividade para neurodivergentes. "
        "Crie checklists limpos, com verbos de ação claros e livres de poluição textual."
    )

    try:
        response = client.models.generate_content(
            model=MODELO_GEMINI,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )
    except Exception as erro:
        logger.exception("Falha ao gerar passos no Gemini")
        raise FalhaIA("Não foi possível gerar os passos agora. Tente novamente.") from erro

    passos = [
        linha.lstrip("0123456789.-* ")
        for linha in _linhas_da_resposta(response)
    ]
    passos = [passo for passo in passos if passo]

    if not passos:
        raise FalhaIA("A IA não retornou nenhum passo.")

    return passos
