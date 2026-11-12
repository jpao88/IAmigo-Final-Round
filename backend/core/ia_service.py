"""Integração com a IA (Gemini). É o único arquivo que conhece o provedor:
para trocar de IA, basta reescrever as funções daqui mantendo o mesmo formato de saída.
"""
import json
import logging
from typing import List

from google import genai
from google.genai import types
from pydantic import BaseModel

from config.settings import settings
from core.erros import FalhaIA

logger = logging.getLogger(__name__)

MODELO_GEMINI = "gemini-2.5-flash"
# Sem resposta em 30 s, a pessoa recebe o aviso e pode escrever os passos à mão (H2.4).
TEMPO_LIMITE_MS = 30_000

client = (
    genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(timeout=TEMPO_LIMITE_MS),
    )
    if settings.gemini_api_key
    else None
)

# Regras do recorrido: de 3 a 7 passos; sem estimativa, um passo vale 10 minutos.
MAXIMO_PASSOS = 7
MINUTOS_PADRAO = 10
MINUTOS_MAXIMO = 120
TAMANHO_MAXIMO_TEXTO = 255  # coluna passos.texto

# O texto dos passos aparece na interface, que é em espanhol.
INSTRUCAO_SISTEMA = (
    "Eres IAmigo, un asistente para adultos con TDAH. "
    "Divides tareas en pasos concretos, pequeños y fáciles de empezar. "
    "Cada paso empieza con un verbo en infinitivo o imperativo, en español, "
    "con menos de diez palabras y sin jerga. Nunca culpas ni presionas."
)


class _PassoIA(BaseModel):
    texto: str
    minutos: int


def _normalizar(passos_brutos) -> List[dict]:
    """Limpa o que a IA devolveu: textos vazios fora, minutos em faixa válida, no máximo 7."""
    passos = []

    for bruto in passos_brutos:
        texto = str(bruto.get("texto", "")).strip().lstrip("0123456789.-*) ").strip()
        if not texto:
            continue

        try:
            minutos = int(bruto.get("minutos"))
        except (TypeError, ValueError):
            minutos = MINUTOS_PADRAO

        if not 1 <= minutos <= MINUTOS_MAXIMO:
            minutos = MINUTOS_PADRAO

        passos.append({"texto": texto[:TAMANHO_MAXIMO_TEXTO], "minutos_estimados": minutos})

    return passos[:MAXIMO_PASSOS]


def gerar_passos_tarefa(titulo_tarefa: str) -> List[dict]:
    """H2.1: divide a tarefa em 3 a 7 passos, cada um com minutos estimados.

    Devolve [{"texto": ..., "minutos_estimados": ...}, ...].
    Qualquer problema vira FalhaIA, e a API responde 503.
    """
    if not client:
        raise FalhaIA("GEMINI_API_KEY não configurada.")

    prompt = (
        "Divide esta tarea en entre 3 y 7 pasos, en el orden en que se hacen. "
        "Para cada paso, estima cuántos minutos toma. Idealmente cada paso dura "
        "entre 5 y 25 minutos: si la tarea es grande, el primer paso debe ser "
        "fácil de empezar. Si la tarea es pequeña, usa pocos pasos y pocos minutos.\n\n"
        f"Tarea: {json.dumps(titulo_tarefa, ensure_ascii=False)}"
    )

    try:
        passos_brutos = _pedir_passos(prompt)
    except Exception as erro:
        logger.exception("Falha ao gerar passos no Gemini")
        raise FalhaIA("Não foi possível gerar os passos agora.") from erro

    if not isinstance(passos_brutos, list):
        raise FalhaIA("A IA não retornou nenhum passo.")

    passos = _normalizar(p for p in passos_brutos if isinstance(p, dict))

    if not passos:
        raise FalhaIA("A IA não retornou nenhum passo.")

    return passos


def _pedir_passos(prompt: str) -> list:
    """Chama o Gemini pedindo uma lista JSON de {texto, minutos}."""
    resposta = client.models.generate_content(
        model=MODELO_GEMINI,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCAO_SISTEMA,
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=list[_PassoIA],
        ),
    )
    return json.loads(resposta.text or "[]")


def dividir_passo(titulo_tarefa: str, texto_passo: str, minutos: int) -> List[dict]:
    """H4.4 "Me atasqué": divide um passo travado em 2 ou 3 passos menores.

    Devolve [{"texto": ..., "minutos_estimados": ...}, ...]; erro vira FalhaIA (503).
    """
    if not client:
        raise FalhaIA("GEMINI_API_KEY não configurada.")

    prompt = (
        "La persona se trabó en este paso y no logra empezarlo. "
        "Divídelo en 2 o 3 pasos más pequeños y concretos, en orden. "
        "El primero debe ser tan fácil que se pueda empezar ya, en menos de 5 minutos. "
        f"Entre todos deberían sumar más o menos {minutos} minutos.\n\n"
        f"Tarea: {json.dumps(titulo_tarefa, ensure_ascii=False)}\n"
        f"Paso trabado: {json.dumps(texto_passo, ensure_ascii=False)}"
    )

    try:
        passos_brutos = _pedir_passos(prompt)
    except Exception as erro:
        logger.exception("Falha ao dividir passo no Gemini")
        raise FalhaIA("Não foi possível dividir o passo agora.") from erro

    if not isinstance(passos_brutos, list):
        raise FalhaIA("A IA não retornou nenhum passo.")

    passos = _normalizar(p for p in passos_brutos if isinstance(p, dict))[:3]

    # Um passo só não ajuda quem travou: precisa de pelo menos 2.
    if len(passos) < 2:
        raise FalhaIA("A IA não retornou passos suficientes.")

    return passos
