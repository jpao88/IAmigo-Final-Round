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

# O texto dos passos aparece na interface: a IA responde no idioma da pessoa.
IDIOMAS = ("es", "pt")

TEXTOS = {
    "es": {
        "instrucao": (
            "Eres IAmigo, un asistente para adultos con TDAH. "
            "Divides tareas en pasos concretos, pequeños y fáciles de empezar. "
            "Cada paso empieza con un verbo en infinitivo o imperativo, en español, "
            "con menos de diez palabras y sin jerga. Nunca culpas ni presionas."
        ),
        "gerar": (
            "Divide esta tarea en entre 3 y 7 pasos, en el orden en que se hacen. "
            "Para cada paso, estima cuántos minutos toma. Idealmente cada paso dura "
            "entre 5 y 25 minutos: si la tarea es grande, el primer paso debe ser "
            "fácil de empezar. Si la tarea es pequeña, usa pocos pasos y pocos minutos.\n\n"
            "Tarea: {titulo}"
        ),
        "dividir": (
            "La persona se trabó en este paso y no logra empezarlo. "
            "Divídelo en 2 o 3 pasos más pequeños y concretos, en orden. "
            "El primero debe ser tan fácil que se pueda empezar ya, en menos de 5 minutos. "
            "Entre todos deberían sumar más o menos {minutos} minutos.\n\n"
            "Tarea: {titulo}\n"
            "Paso trabado: {passo}"
        ),
    },
    "pt": {
        "instrucao": (
            "Você é o IAmigo, um assistente para adultos com TDAH. "
            "Você divide tarefas em passos concretos, pequenos e fáceis de começar. "
            "Cada passo começa com um verbo no infinitivo ou no imperativo, em português do Brasil, "
            "com menos de dez palavras e sem jargão. Você nunca culpa nem pressiona."
        ),
        "gerar": (
            "Divida esta tarefa em 3 a 7 passos, na ordem em que são feitos. "
            "Para cada passo, estime quantos minutos leva. O ideal é que cada passo dure "
            "entre 5 e 25 minutos: se a tarefa for grande, o primeiro passo deve ser "
            "fácil de começar. Se a tarefa for pequena, use poucos passos e poucos minutos.\n\n"
            "Tarefa: {titulo}"
        ),
        "dividir": (
            "A pessoa travou neste passo e não consegue começar. "
            "Divida-o em 2 ou 3 passos menores e concretos, em ordem. "
            "O primeiro deve ser tão fácil que dê para começar agora, em menos de 5 minutos. "
            "Juntos, devem somar mais ou menos {minutos} minutos.\n\n"
            "Tarefa: {titulo}\n"
            "Passo travado: {passo}"
        ),
    },
}


def _textos(idioma: str) -> dict:
    return TEXTOS.get(idioma, TEXTOS["es"])


def montar_prompt_gerar(titulo_tarefa: str, idioma: str = "es") -> str:
    return _textos(idioma)["gerar"].format(titulo=json.dumps(titulo_tarefa, ensure_ascii=False))


def montar_prompt_dividir(titulo_tarefa: str, texto_passo: str, minutos: int, idioma: str = "es") -> str:
    return _textos(idioma)["dividir"].format(
        titulo=json.dumps(titulo_tarefa, ensure_ascii=False),
        passo=json.dumps(texto_passo, ensure_ascii=False),
        minutos=minutos,
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


def gerar_passos_tarefa(titulo_tarefa: str, idioma: str = "es") -> List[dict]:
    """H2.1: divide a tarefa em 3 a 7 passos, cada um com minutos estimados.

    Devolve [{"texto": ..., "minutos_estimados": ...}, ...].
    Qualquer problema vira FalhaIA, e a API responde 503.
    """
    if not client:
        raise FalhaIA("GEMINI_API_KEY não configurada.")

    try:
        passos_brutos = _pedir_passos(montar_prompt_gerar(titulo_tarefa, idioma), idioma)
    except Exception as erro:
        logger.exception("Falha ao gerar passos no Gemini")
        raise FalhaIA("Não foi possível gerar os passos agora.") from erro

    if not isinstance(passos_brutos, list):
        raise FalhaIA("A IA não retornou nenhum passo.")

    passos = _normalizar(p for p in passos_brutos if isinstance(p, dict))

    if not passos:
        raise FalhaIA("A IA não retornou nenhum passo.")

    return passos


def _pedir_passos(prompt: str, idioma: str = "es") -> list:
    """Chama o Gemini pedindo uma lista JSON de {texto, minutos}."""
    resposta = client.models.generate_content(
        model=MODELO_GEMINI,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_textos(idioma)["instrucao"],
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=list[_PassoIA],
        ),
    )
    return json.loads(resposta.text or "[]")


def dividir_passo(titulo_tarefa: str, texto_passo: str, minutos: int, idioma: str = "es") -> List[dict]:
    """H4.4 "Me atasqué": divide um passo travado em 2 ou 3 passos menores.

    Devolve [{"texto": ..., "minutos_estimados": ...}, ...]; erro vira FalhaIA (503).
    """
    if not client:
        raise FalhaIA("GEMINI_API_KEY não configurada.")

    try:
        passos_brutos = _pedir_passos(montar_prompt_dividir(titulo_tarefa, texto_passo, minutos, idioma), idioma)
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
