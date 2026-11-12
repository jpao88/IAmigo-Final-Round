import os
import re
import tempfile

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import settings

# URL.create escapa caracteres especiais da senha (@, :, /, #...),
# que quebrariam uma URL montada com f-string.
DATABASE_URL = URL.create(
    "mysql+mysqlconnector",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)


def _gravar_certificado(conteudo: str) -> str:
    """Grava o certificado recebido numa variável (DB_SSL_CA_PEM) num arquivo temporário.

    Painéis de hosting às vezes juntam as linhas ou trocam quebras por espaços;
    por isso o certificado é remontado a partir do bloco base64.
    """
    # "\n" escrito como texto (barra + n) também conta como quebra de linha.
    conteudo = conteudo.replace("\\n", "\n")
    blocos = re.findall(
        r"-----BEGIN CERTIFICATE-----(.+?)-----END CERTIFICATE-----", conteudo, re.S
    )
    if not blocos:
        raise RuntimeError("DB_SSL_CA_PEM não contém um certificado (BEGIN/END CERTIFICATE).")

    pem = ""
    for bloco in blocos:
        corpo = re.sub(r"\s+", "", bloco)
        linhas = [corpo[i:i + 64] for i in range(0, len(corpo), 64)]
        pem += "-----BEGIN CERTIFICATE-----\n" + "\n".join(linhas) + "\n-----END CERTIFICATE-----\n"

    arquivo = tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False, encoding="ascii")
    with arquivo:
        arquivo.write(pem)
    return arquivo.name


def _argumentos_ssl() -> dict:
    """Com DB_SSL_CA (arquivo) ou DB_SSL_CA_PEM (conteúdo), exige SSL e verifica
    o certificado do servidor (Aiven)."""
    if settings.db_ssl_ca_pem:
        return {"ssl_ca": _gravar_certificado(settings.db_ssl_ca_pem), "ssl_verify_cert": True}

    if not settings.db_ssl_ca:
        return {}

    if not os.path.isfile(settings.db_ssl_ca):
        raise RuntimeError(f"DB_SSL_CA aponta para um arquivo que não existe: '{settings.db_ssl_ca}'.")

    return {"ssl_ca": settings.db_ssl_ca, "ssl_verify_cert": True}


engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=_argumentos_ssl())

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()
