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

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()
