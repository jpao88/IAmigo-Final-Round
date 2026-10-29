import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from config.settings import settings

ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000

ALGORITMO_TOKEN = "HS256"


def gerar_hash_senha(senha: str) -> str:
    """Gera um hash com sal aleatório. A senha original nunca é guardada."""
    sal = secrets.token_bytes(16)
    resumo = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), sal, ITERACOES)
    return f"{ALGORITMO}${ITERACOES}${sal.hex()}${resumo.hex()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Recalcula o hash da senha recebida e compara com o guardado."""
    try:
        algoritmo, iteracoes, sal_hex, resumo_hex = senha_hash.split("$")

        if algoritmo != ALGORITMO:
            return False

        resumo = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            bytes.fromhex(sal_hex),
            int(iteracoes)
        )
    except (AttributeError, ValueError):
        return False

    return hmac.compare_digest(resumo.hex(), resumo_hex)


def _obter_segredo() -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET não configurado no .env.")

    return settings.jwt_secret


def gerar_token_acesso(usuario_id: int, nome: str):
    """Gera um JWT assinado. Devolve o token e sua duração em segundos."""
    segredo = _obter_segredo()
    minutos = settings.jwt_expira_minutos
    agora = datetime.now(timezone.utc)

    payload = {
        "sub": str(usuario_id),
        "nome": nome,
        "iat": agora,
        "exp": agora + timedelta(minutes=minutos)
    }

    token = jwt.encode(payload, segredo, algorithm=ALGORITMO_TOKEN)
    return token, minutos * 60



def validar_token_acesso(token: str) -> int:
    """Valida assinatura e expiração. Devolve o id do usuário (sub)."""
    segredo = _obter_segredo()

    try:
        payload = jwt.decode(
            token,
            segredo,
            algorithms=[ALGORITMO_TOKEN],
            options={"require": ["sub", "exp"]}
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        raise ValueError("Token inválido ou expirado.")