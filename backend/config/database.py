import os

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


def _argumentos_ssl() -> dict:
    """Com DB_SSL_CA, exige SSL e verifica o certificado do servidor (Aiven)."""
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
