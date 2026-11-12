"""Configurações do sistema, lidas do .env uma única vez.

Qualquer módulo que precise de uma configuração importa `settings` daqui,
em vez de chamar os.getenv. Assim o .env é carregado antes de qualquer
leitura, não importa a ordem dos imports.
"""
import os
from dataclasses import dataclass, field
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()

ORIGENS_PADRAO = (
    "http://localhost:5500,"
    "http://127.0.0.1:5500,"
    "http://localhost:5173,"
    "http://127.0.0.1:5173"
)


def _lista(valor: str) -> List[str]:
    return [item.strip() for item in valor.split(",") if item.strip()]


def _inteiro(nome: str, padrao: str) -> int:
    valor = os.getenv(nome, padrao)

    try:
        return int(valor)
    except ValueError:
        raise RuntimeError(f"{nome} precisa ser um número inteiro (valor atual: '{valor}').")


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = _inteiro("DB_PORT", "3306")
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "iamigo")
    # Caminho do ca.pem (Aiven). Vazio = conexão sem SSL (MySQL local).
    db_ssl_ca: Optional[str] = os.getenv("DB_SSL_CA") or None

    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY") or None

    # Obrigatório para o login da API (core/seguranca.py).
    jwt_secret: Optional[str] = os.getenv("JWT_SECRET") or None
    jwt_expira_minutos: int = _inteiro("JWT_EXPIRA_MINUTOS", "60")

    cors_origins: List[str] = field(
        default_factory=lambda: _lista(os.getenv("CORS_ORIGINS", ORIGENS_PADRAO))
    )
    # Opcional, só para testar no celular na rede de casa: um padrão (regex) de origens.
    cors_origem_regex: Optional[str] = os.getenv("CORS_ORIGIN_REGEX") or None


settings = Settings()
