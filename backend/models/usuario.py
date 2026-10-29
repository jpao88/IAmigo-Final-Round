from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Enum, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from config.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    papel: Mapped[str] = mapped_column(
        Enum("usuario", "admin", name="papel_enum"),
        nullable=False,
        default="usuario",
        server_default="usuario",
    )
    limite_hoje: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=3, server_default="3"
    )
    onboarding_concluido: Mapped[bool] = mapped_column(
        nullable=False, default=False, server_default="0"
    )
    criado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())

    # passive_deletes: quem apaga as tarefas e os fechamentos é o ON DELETE CASCADE do banco.
    tarefas: Mapped[List["Tarefa"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Tarefa.id",
    )
    fechamentos: Mapped[List["FechamentoDia"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="FechamentoDia.data",
    )
